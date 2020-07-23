# Deploy presidio as a system

You can install Presidio locally using [Docker](https://www.docker.com/) or [KIND](https://github.com/kubernetes-sigs/kind), as a service in [Kubernetes](https://kubernetes.io/) or [AKS](https://docs.microsoft.com/en-us/azure/aks/intro-kubernetes) or use it as a framework in a python application.

Decide on a name for your Presidio project. In the [examples](samples.md) the project name is `<my-project>`.

- Development and Testing
  - [Deploy locally using Docker](#the-easy-way-with-docker)
  - [Deploy locally using KIND](#deploy-locally-with-kind)
  - [Presidio-Analyzer as a standalone python package](#install-presidio-analyzer-as-a-python-package)
- [Production - Deploy with Kubernetes](#presidio-as-a-service-with-kubernetes)
  - [Prerequisites](#prerequisites)
  - [Single click deployment](#single-click-deployment)
  - [Step by Step Deployment with customizable parameters](#step-by-step-deployment-with-customizable-parameters)

## The easy way with Docker

You will need to have Docker installed and running, and [make](https://www.gnu.org/software/make/) installed on your system.

Sync this repo use `make` to build and deploy locally.

For convenience the script [build.sh](../build.sh) at the root of this repo will run the `make` commands for you. If you use the script remember to make it executable by running `chmod +x build.sh` after syncing the code.

**NOTE: Building the deps images currently takes some time** (~70 minutes, depending on the build machine). We are working on improving the build time through improving the build and providing pre-built dependencies.

**NOTE: Error message** You may see error messages like this:

`Error response from daemon: pull access denied for presidio/presidio-golang-deps, repository does not exist or may require 'docker login': denied: requested access to the resource is denied`
when running the `make` commands. These can be ignored.

**NOTE: Memory requirements** if you get an error message like this

`tests/test_analyzer_engine.py ...............The command '/bin/sh -c pipenv run pytest' returned a non-zero code: 137`

while building you may need to increase the docker memory limit for your machine

### Validation

Once the build is complete you can verify the local deployment by running:

```sh
docker ps
```

You should see 4 Presidio containers and one Redis container running with the following names:

```sh
presidio-api
presidio-recognizers-store
presidio-anonymizer
presidio-analyzer
redis
```

## Deploy locally with KIND

Presidio is built for Kubernetes, you can give it a try using [KIND (Kubernetes IN Docker)](https://github.com/kubernetes-sigs/kind).

1. Install [Docker](https://docs.docker.com/install/).

   - **Optional (Linux)** - the following command will install all prerequisites (Docker, Helm, make, kubetl).

     ```sh
     cd deployment/
     ./prerequisites.sh
     ```

     depending on your environment, sudo might be needed

2. Clone Presidio.

3. Run the following script, which will use KIND (Kubernetes emulation in Docker)

   ```sh
   cd deployment/
   ./run-with-kind.sh
   ```

4. Wait and verify all pods are running:

   ```sh
   kubectl get pod -n presidio
   ```

5. Port forwarding of HTTP requests to the API micro-service will be done automatically. In order to run manual:
   ```sh
   kubectl port-forward <presidio-api-pod-name> 8080:8080 -n presidio
   ```

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
from presidio_analyzer import AnalyzerEngine

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

## Presidio As a Service with Kubernetes

### Prerequisites

1. A Kubernetes 1.9+ cluster with [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) enabled. If you are using [AKS](https://docs.microsoft.com/en-us/azure/aks/intro-kubernetes) RBAC is enabled by default.

   - Note the pod's resources requirements (CPU and memory) and plan the cluster accordingly.

2. [kubectl](https://kubernetes.io/docs/reference/kubectl/overview/) installed

   - verify you can communicate with the cluster by running:

     ```sh
     kubectl version
     ```

3. Local [helm](https://helm.sh/) client.
4. **Optional** - Container Registry - such as [ACR](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-intro). Only needed if you are using your own presidio images and not the default ones from from [Microsoft syndicates container catalog](https://azure.microsoft.com/en-in/blog/microsoft-syndicates-container-catalog/)
5. Recent presidio repo is cloned on your local machine.

### Single click deployment

1. Navigate into `<root>\deployment` from command line.

2. If You have helm installed, but havn't run `helm init`, execute [deploy-helm.sh](../deployment/deploy-helm.sh) in the command line. It will install `tiller` (helm server side) on your cluster, and grant it sufficient permissions. Note that this script uses Helm 2 version.

```sh
deploy-helm.sh
```

3. Optional - Grant the Kubernetes cluster access to the container registry. Only needed if you will use your own presidio images. This step can be skipped and the script will pull the container images from [Microsoft syndicates container catalog](https://azure.microsoft.com/en-in/blog/microsoft-syndicates-container-catalog/)

   - If using Azure Kubernetes Service, follow these instructions to [grant the AKS cluster access to the ACR.](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-auth-aks)

4. If you already have `helm` and `tiller` configured, or if you installed it in the previous step, execute [deploy-presidio.sh](../deployment/deploy-presidio.sh) in the command line as follows:

```sh
deploy-presidio.sh
```

The script will install Presidio on your cluster using the default values.

> Note: You can edit the file to use your own container registry and image.

### Step by step deployment with customizable parameters

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

6. For more deployment options, follow the [Development guide](https://github.com/Microsoft/presidio/blob/master/docs/development.md)
