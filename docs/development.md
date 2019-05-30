# Development

## Setting up the environment - Golang

1. Docker

***Note that the port mapping will conflict with running `make test`***

2. Redis

    ```sh
    docker run --name dev-redis -d -p 6379:6379 redis
    ```

3. Install go 1.11 and Python 3.7

4. Install the golang packages via [dep](https://github.com/golang/dep/releases)

    ```sh
    dep ensure
    ```

5. Install [tesseract](https://github.com/tesseract-ocr/tesseract/wiki) OCR framework.

6. Protobuf generator tools (Optional)

    - `https://github.com/golang/protobuf`

    - `https://grpc.io/docs/tutorials/basic/python.html`

    To generate proto files, clone [presidio-genproto](https://github.com/Microsoft/presidio-genproto) and run the following commands in `$GOPATH/src/github.com/Microsoft/presidio-genproto/src` folder

    ```sh
    python -m grpc_tools.protoc -I . --python_out=../python --grpc_python_out=../python ./*.proto
    ```

    ```sh
    protoc -I . --go_out=plugins=grpc:../golang ./*.proto
    ```

## Setting up the environment - Python

1. Build and install [re2](https://github.com/google/re2)

    ```sh
    re2_version="2018-12-01"
    wget -O re2.tar.gz https://github.com/google/re2/archive/${re2_version}.tar.gz
    mkdir re2 
    tar --extract --file "re2.tar.gz" --directory "re2" --strip-components 1
    cd re2 && make install
    ```

2. Install pipenv

    [Pipenv](https://pipenv.readthedocs.io/en/latest/) is a Python workflow manager, handling dependencies and environment for python packages, it is used in the Presidio's Analyzer project as the dependencies manager
    #### Using Pip3:
    ```
    pip3 install --user pipenv
    ```
    #### Homebrew
    ```
    brew install pipenv
    ```

    Additional installation instructions: https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv

3. Create virtualenv for the project & Install all requirements in the Pipfile, including dev requirements
Install the Python packages for the analyzer in the `presidio-analyzer` folder, run:
    ```
    pipenv install --dev --sequential
    ```

4. Run all tests
    ```
    pipenv run pytest
    ```

5. To run arbitrary scripts within the virtual env, start the command with `pipenv run`. For example:
    1. `pipenv run flake8 analyzer --exclude "*pb2*.py"`
    2. `pipenv run pylint analyzer`
    3. `pipenv run pip freeze`

#### Alternatively, activate the virtual environment and use the commands by starting a pipenv shell:

1. Start shell:

    ```
    pipenv shell
    ```
2. Run commands in the shell

    ```
    pytest
    pylint analyzer
    pip freeze
    ```

## Development notes

- Build the bins with `make build`
- Build the base containers with `make docker-build-deps DOCKER_REGISTRY=${DOCKER_REGISTRY} PRESIDIO_DEPS_LABEL=${PRESIDIO_DEPS_LABEL}`
- Build the the Docker image with `make docker-build DOCKER_REGISTRY=${DOCKER_REGISTRY} PRESIDIO_DEPS_LABEL=${PRESIDIO_DEPS_LABEL} PRESIDIO_LABEL=${PRESIDIO_LABEL}`
- Push the Docker images with `make docker-push DOCKER_REGISTRY=${DOCKER_REGISTRY} PRESIDIO_LABEL=${PRESIDIO_LABEL}`
- Run the tests with `make test`
- Adding a file in go requires the `make go-format` command before running and building the service.
- Run functional tests with `make test-functional`
- Updating python dependencies [instructions](./pipenv_readme.md)

### Set the following environment variables

#### presidio-analyzer

- `GRPC_PORT`: `3001` GRPC listen port

#### presidio-anonymizer

- `GRPC_PORT`: `3002` GRPC listen port

#### presidio-api

- `WEB_PORT`: `8080` HTTP listen port
- `REDIS_URL`: `localhost:6379`, Optional: Redis address
- `ANALYZER_SVC_ADDRESS`: `localhost:3001`, Analyzer address
- `ANONYMIZER_SVC_ADDRESS`: `localhost:3002`, Anonymizer address

### Developing only for Presidio Analyzer under Windows environment
Run locally the core services Presidio needs to operate:
```
docker run --rm --name test-redis --network testnetwork -d -p 6379:6379 redis
docker run --rm --name test-presidio-anonymizer --network testnetwork -d -p 3001:3001 -e GRPC_PORT=3001 mcr.microsoft.com/presidio-anonymizer:latest
docker run --rm --name test-presidio-recognizers-store --network testnetwork -d -p 3004:3004 -e GRPC_PORT=3004 -e REDIS_URL=test-redis:6379 mcr.microsoft.com/presidio-recognizers-store:latest
```
Naviagate to `<Presidio folder>\presidio-analyzer\`

Install the python packages if didn't do so yet:
```sh
pipenv install --dev --sequential
```

To simply run unit tests, execute:
```
pipenv run pytest --log-cli-level=0
```

If you want to experiment with `analyze` requests, navigate into the `analyzer` folder and start serving the analyzer service:
```sh
pipenv run python __main__.py serve --grpc-port 3000
```

In a new `pipenv shell` window you can run `analyze` requests, for example:
```
pipenv run python __main__.py analyze --text "John Smith drivers license is AC432223" --fields "PERSON" "US_DRIVER_LICENSE" --grpc-port 3000
```



## Load test

1. Edit  `post.lua`. Change the template name
2. Run [wrk](https://github.com/wg/wrk)

    ```sh
    wrk -t2 -c2 -d30s -s post.lua http://<api-service-address>/api/v1/projects/<my-project>/analyze
    ```


## Running in kubernetes

1. If deploying from a private registry, verify that Kubernetes has access to the [Docker Registry](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-auth-aks).

2. If using a Kubernetes secert to manage the registry authentication, make sure it is registered under 'presidio' namespace

### Further configuration

Edit [charts/presidio/values.yaml](../charts/presidio/values.yaml) to:
- Setup secret name (for private registries)
- Change presidio services version
- Change default scale
