# Install (deploy) presidio as a system

You can install Presidio locally using [Docker](https://www.docker.com/), as a service in [Kubernetes](https://kubernetes.io/) or use it as a framework in a python application.

## The easy way with Docker

You will need to have Docker installed and running, and [make](https://www.gnu.org/software/make/) installed on your system.

Sync this repo use `make` to build and deploy locally.

For convenience the script `build.sh` at the root of this repo will run the `make` commands for you. If you use the script remember to make it executable by running `chmod +x build.sh` after syncing the code.

**NOTE: Building the deps images currently takes some time** (~70 minutes, depending on the build machine). We are working on improving the build time through improving the build and providing pre-built dependencies.

**NOTE: Error message** You may see error messages like this:
`Error response from daemon: pull access denied for presidio/presidio-golang-deps, repository does not exist or may require 'docker login': denied: requested access to the resource is denied` when running the `make` commands. These can be ignored.

**NOTE: Memory requirements** if you get an error message like this
`tests/test_analyzer_engine.py ...............The command '/bin/sh -c pipenv run pytest' returned a non-zero code: 137`
while building you may need to increase the docker memory limit for your machine

If you prefer to run each step by hand instead of using the `build.sh` script these are as follows:

```sh
# Build the images

export DOCKER_REGISTRY=presidio
export PRESIDIO_LABEL=latest
make DOCKER_REGISTRY=${DOCKER_REGISTRY} PRESIDIO_LABEL=${PRESIDIO_LABEL} docker-build-deps
make DOCKER_REGISTRY=${DOCKER_REGISTRY} PRESIDIO_LABEL=${PRESIDIO_LABEL} docker-build

# Run the containers

docker network create mynetwork
docker run --rm --name redis --network mynetwork -d -p 6379:6379 redis
docker run --rm --name presidio-analyzer --network mynetwork -d -p 3000:3000 -e GRPC_PORT=3000 -e RECOGNIZERS_STORE_SVC_ADDRESS=presidio-recognizers-store:3004 $(DOCKER_REGISTRY)/presidio-analyzer:$(PRESIDIO_LABEL)
docker run --rm --name presidio-anonymizer --network mynetwork -d -p 3001:3001 -e GRPC_PORT=3001 $(DOCKER_REGISTRY)/presidio-anonymizer:$(PRESIDIO_LABEL)
docker run --rm --name presidio-recognizers-store --network mynetwork -d -p 3004:3004 -e GRPC_PORT=3004 -e REDIS_URL=redis:6379 $(DOCKER_REGISTRY)/presidio-recognizers-store:$(PRESIDIO_LABEL)

sleep 30 # Wait for the analyzer model to load
docker run --rm --name presidio-api --network mynetwork -d -p 8080:8080 -e WEB_PORT=8080 -e ANALYZER_SVC_ADDRESS=presidio-analyzer:3000 -e ANONYMIZER_SVC_ADDRESS=presidio-anonymizer:3001 -e RECOGNIZERS_STORE_SVC_ADDRESS=presidio-recognizers-store:3004 $(DOCKER_REGISTRY)/presidio-api:$(PRESIDIO_LABEL)
```

Once the build is complete you can verify the local deployment by running `docker ps`. You should see 4 Presidio containers and one Redis container running with the following names:

```sh
presidio-api
presidio-recognizers-store
presidio-anonymizer
presidio-analyzer
redis
```

---

## Presidio As a Service with Kubernetes

### Requirements

- Kubernetes 1.9+ with RBAC enabled.
  - Note the pod's resources requirements (CPU and memory) and plan the cluster accordingly.
- Helm

### Default installation using pre-made scripts

Follow the installation guide at the [Readme page](https://github.com/Microsoft/presidio/blob/master/README.MD)

### Step-by step installation with customizable parameters

1. Install [Helm](https://github.com/kubernetes/helm) with [RBAC](https://github.com/kubernetes/helm/blob/master/docs/rbac.md#tiller-and-role-based-access-control)

2. Install [Redis](https://hub.kubeapps.com/charts/stable/redis) (Cache for storage and database scanners)

   ```sh
   helm install --name redis stable/redis --set usePassword=false,rbac.create=true --namespace presidio-system
   ```

3. Optional - Ingress controller for presidio API.

   - [Traefik](https://docs.traefik.io/user-guide/kubernetes/)
   - [NGINX](https://docs.microsoft.com/en-us/azure/aks/ingress-tls)
   - [Istio](https://istio.io/docs/tasks/traffic-management/ingress/)

   **Note** that presidio is not deployed with an ingress controller by default.  
   to change this behavior, deploy the helm chart with _api.ingress.enabled=true_ and specify they type of ingress controller to be used with _api.ingress.class=nginx_ (supported classes are: nginx, traefik or istio).

4. Verify that Redis and Traefik/NGINX are installed correctly

5. Deploy from `/charts/presidio`

   ```sh
   # Based on the DOCKER_REGISTRY and PRESIDIO_LABEL from the previous steps
   helm install --name presidio-demo --set registry=${DOCKER_REGISTRY},tag=${PRESIDIO_LABEL} . --namespace presidio
   ```

6. For more options over the deployment, follow the [Development guide](https://github.com/Microsoft/presidio/blob/master/docs/development.md)

## Install presidio-analyzer as a Python package

If you're interested in running the analyzer alone, you can install it as a standalone python package by packaging it into a `wheel` file. Note that Presidio requires Python >= 3.6.

#### Creating the wheel file:

In the presidio-analyzer folder, run:

```sh
python setup.py bdist_wheel
```

#### Installing the wheel file

1. Copy the created wheel file (from the `dist` folder of presidio-analyzer) into a clean virtual environment

2. install `wheel` package

```sh
pip install wheel
```

2. Install the presidio-analyzer wheel file

```sh
pip install WHEEL_FILE
```

Where `WHEEL_FILE` is the path to the created wheel file

3. Install the Spacy model from Github (not installed during the standard installation)

```sh
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-2.1.0/en_core_web_lg-2.1.0.tar.gz
```

Note that if you skip this step, the Spacy model would install lazily during the first call to the `AnalyzerEngine`

4. _Optional_ : install `re2` and `pyre2`:

- Install [re2](https://github.com/google/re2):

  ```sh
  re2_version="2018-12-01"
  wget -O re2.tar.gz https://github.com/google/re2/archive/${re2_version}.tar.gz
  mkdir re2
  tar --extract --file "re2.tar.gz" --directory "re2" --strip-components 1
  cd re2 && make install
  ```

- Install `pyre2`'s fork:

  ```
  pip install https://github.com/torosent/pyre2/archive/release/0.2.23.zip
  ```

  Note: If you don't install `re2`, Presidio will use the `regex` package for regular expressions handling

5. Test the installation

To test, run Python on the virtual env you've installed the presidio-analyzer in.
Then, make sure this code returns an answer:

```python
from analyzer import AnalyzerEngine

engine = AnalyzerEngine()

text = "My name is David and I live in Miami"

response = engine.analyze(correlation_id=0,
                          text = text,
                          entities=[],
                          language='en',
                          all_fields=True,
                          score_threshold=0.5)

for item in response:
    print("Start = {}, end = {}, entity = {}, confidence = {}".format(item.start,
                                                                      item.end,
                                                                      item.entity_type,
                                                                      item.score))

```
