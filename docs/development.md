# Setting Up a Development Environment

Most of Presidio's services are written in Go. The `presidio-analyzer` module, in charge of detecting entities in text, is written in Python. This document details the required parts for developing for Presidio.

## Table of contents

1. [Setting up the Go environment](#dev-go)
2. [Setting up the Python environment](#dev-python)
3. [Development notes](#dev-notes)
   1. [General notes](#dev-general-notes)
   2. [Setting up environment variables](#env-variables)
   3. [Developing on Windows](#develop-windows)

## Setting up the Go environment <a name='dev-go'></a>

1. Install go 1.11 and Python 3.7

2. Install the golang packages via [dep](https://github.com/golang/dep/releases)

   ```sh
   dep ensure
   ```

3. Install [tesseract](https://github.com/tesseract-ocr/tesseract/wiki) OCR framework. (**Optional**, only for Image anonymization)

## Setting up the Python environment <a name='dev-python'></a>

1. Build and install [re2](https://github.com/google/re2) (**Optional**. Presidio will use `regex` instead of `pyre2` if `re2` is not installed)

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

3. Create virtualenv for the project and install all requirements in the Pipfile, including dev requirements. In the `presidio-analyzer` folder, run:
    ```
    pipenv install --dev --sequential --skip-lock
    ```

4. Download spacy model
    ```
    pipenv run python -m spacy download en_core_web_lg
    ```

5. Run all tests
    ```
    pipenv run pytest
    ```

6. To run arbitrary scripts within the virtual env, start the command with `pipenv run`. For example:
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

- To use presidio-analyzer as a python library, see [Installing presidio-analyzer as a standalone Python package](https://github.com/microsoft/presidio/blob/master/docs/deploy.md#install-presidio-analyzer-as-a-python-package)
- To add new recognizers in order to support new entities, see [Adding new custom recognizers](https://github.com/microsoft/presidio/blob/master/docs/custom_fields.md)

## Development notes <a name='dev-notes'></a>

### General notes <a name="dev-general-notes"></a>

- Installing and building the entire Presidio solution is currently not supported on Windows. However, installing and building the different docker images, or the Python package for detecting entities (presidio-analyzer) is possible on Windows. See [here](#develop-windows)
- Build the bins with `make build`
- Build the base containers with `make docker-build-deps DOCKER_REGISTRY=${DOCKER_REGISTRY} PRESIDIO_DEPS_LABEL=${PRESIDIO_DEPS_LABEL}` (If you do not specify a valid, logged-in, registry a warning will echo to the standard output)
- Build the the Docker image with `make docker-build DOCKER_REGISTRY=${DOCKER_REGISTRY} PRESIDIO_DEPS_LABEL=${PRESIDIO_DEPS_LABEL} PRESIDIO_LABEL=${PRESIDIO_LABEL}`
- Push the Docker images with `make docker-push DOCKER_REGISTRY=${DOCKER_REGISTRY} PRESIDIO_LABEL=${PRESIDIO_LABEL}`
- Run the tests with `make test`
- Adding a file in go requires the `make go-format` command before running and building the service.
- Run functional tests with `make test-functional`
- Updating python dependencies [instructions](./pipenv_readme.md)
- These steps are verified on every pull request validation to a presidio branch. do not alter this document without referring to the implemented steps in the [pipeline](../pipelines/templates/build-test-publish.yaml)

### Set the following environment variables <a name="env-variables"></a>

#### presidio-analyzer

- `GRPC_PORT`: `3001` GRPC listen port

#### presidio-anonymizer

- `GRPC_PORT`: `3002` GRPC listen port

#### presidio-api

- `WEB_PORT`: `8080` HTTP listen port
- `REDIS_URL`: `localhost:6379`, Optional: Redis address
- `ANALYZER_SVC_ADDRESS`: `localhost:3001`, Analyzer address
- `ANONYMIZER_SVC_ADDRESS`: `localhost:3002`, Anonymizer address

### Developing only for Presidio Analyzer under Windows environment <a name="develop-windows"></a>

Developing presidio as a whole on Windows is currently not supported. However, it is possible to run and test the presidio-analyzer module, in charge of detecting entities in text, on Windows using Docker:

1. Run locally the core services Presidio needs to operate:

```
docker run --rm --name test-redis --network testnetwork -d -p 6379:6379 redis
docker run --rm --name test-presidio-anonymizer --network testnetwork -d -p 3001:3001 -e GRPC_PORT=3001 mcr.microsoft.com/presidio-anonymizer:latest
docker run --rm --name test-presidio-recognizers-store --network testnetwork -d -p 3004:3004 -e GRPC_PORT=3004 -e REDIS_URL=test-redis:6379 mcr.microsoft.com/presidio-recognizers-store:latest
```

2. Navigate to `<Presidio folder>/presidio-analyzer`

3. Install the python packages if didn't do so yet:

```sh
pipenv install --dev --sequential
```

3. If you want to experiment with `analyze` requests, navigate into the `analyzer` folder and start serving the analyzer service:

```sh
pipenv run python app.py serve --grpc-port 3000
```

4. In a new `pipenv shell` window you can run `analyze` requests, for example:

```
pipenv run python app.py analyze --text "John Smith drivers license is AC432223" --fields "PERSON" "US_DRIVER_LICENSE" --grpc-port 3000
```

## Load test

1. Edit `post.lua`. Change the template name
2. Run [wrk](https://github.com/wg/wrk)

   ```sh
   wrk -t2 -c2 -d30s -s post.lua http://<api-service-address>/api/v1/projects/<my-project>/analyze
   ```

## Running in kubernetes

1. If deploying from a private registry, verify that Kubernetes has access to the [Docker Registry](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-auth-aks).

2. If using a Kubernetes secret to manage the registry authentication, make sure it is registered under 'presidio' namespace

### Further configuration

Edit [charts/presidio/values.yaml](../charts/presidio/values.yaml) to:

- Setup secret name (for private registries)
- Change presidio services version
- Change default scale


## NLP Engine Configuration

1. The nlp engines deployed are set on start up based on the yaml configuration files in `presidio-analyzer/conf/`.  The default nlp engine is the large English SpaCy model (`en_core_web_lg`) set in `default.yaml`.

2. The format of the yaml file is as follows:

```yaml
nlp_engine_name: spacy  # {spacy, stanza}
models:
  -
    lang_code: en  # code corresponds to `supported_language` in any custom recognizers
    model_name: en_core_web_lg  # the name of the SpaCy or Stanza model
  -
    lang_code: de  # more than one model is optional, just add more items
    model_name: de
```

3. By default, we call the method `load_predefined_recognizers` of the `RecognizerRegistry` class to load language specific and language agnostic recognizers.

4. Downloading additional engines.
  * SpaCy NLP Models: [models download page](https://spacy.io/usage/models)
  * Stanza NLP Models: [models download page](https://stanfordnlp.github.io/stanza/available_models.html)

  ```sh
  # download models - tldr
  # spacy
  python -m spacy download en_core_web_lg
  # stanza
  python -c 'import stanza; stanza.download("en");'
  ```
