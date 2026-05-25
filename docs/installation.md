# Installing Presidio

## Description

This document describes the installation of the entire
Presidio suite using `pip` (as Python packages) or using `Docker` (As containerized services).

## Using pip

!!! note "Note"

    Consider installing the Presidio python packages
    in a virtual environment like [venv](https://docs.python.org/3/tutorial/venv.html)
    or [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

### Supported Python Versions

Presidio is supported for the following python versions:

* 3.10
* 3.11
* 3.12
* 3.13

### PII anonymization on text

For PII anonymization on text, install the `presidio-analyzer` and `presidio-anonymizer` packages
with at least one NLP engine (`spaCy`, `transformers` or `stanza`):

===+ "spaCy (default)"

    ```
    pip install presidio_analyzer
    pip install presidio_anonymizer
    python -m spacy download en_core_web_lg
    ```

=== "Transformers"

    ```
    pip install "presidio_analyzer[transformers]"
    pip install presidio_anonymizer
    python -m spacy download en_core_web_sm
    ```

    !!! note "Note"
        
        When using a transformers NLP engine, Presidio would still use spaCy for other capabilities,
        therefore a small spaCy model (such as en_core_web_sm) is required. 
        Transformers models would be loaded lazily. To pre-load them, see: [Downloading a pre-trained model](./analyzer/nlp_engines/transformers.md#downloading-a-pre-trained-model)

=== "Stanza"

    ```
    pip install "presidio_analyzer[stanza]"
    pip install presidio_anonymizer
    ```


    !!! note "Note"
        
        Stanza models would be loaded lazily. To pre-load them, see: [Downloading a pre-trained model](./analyzer/nlp_engines/spacy_stanza.md#download-the-pre-trained-model).

### GPU acceleration (optional)

For GPU acceleration, install the appropriate dependencies for your hardware:

- **Linux with NVIDIA GPU**: `pip install "spacy[cuda12x]"` (or the version matching your CUDA installation)
- **macOS with Apple Silicon**: MPS is detected automatically, no additional dependencies required.

For detailed GPU setup, verification, and troubleshooting, see [GPU Acceleration](./analyzer/nlp_engines/gpu_usage.md).

### PII redaction in images

For PII redaction in images

1. Install the `presidio-image-redactor` package:

    ```sh
    pip install presidio_image_redactor
    
    # Presidio image redactor uses the presidio-analyzer
    # which requires a spaCy language model:
    python -m spacy download en_core_web_lg
    ```

2. Install an OCR engine. The default version uses the [Tesseract OCR Engine](https://github.com/tesseract-ocr/tesseract).
More information on installation can be found [here](image-redactor/index.md#installation).

## Using Docker

Presidio can expose REST endpoints for each service using Flask and Docker.
To download the Presidio Docker containers, run the following command:

!!! note "Note"

    This requires Docker to be installed. [Download Docker](https://docs.docker.com/get-docker/).

### For PII anonymization in text

For PII detection and anonymization in text, the `presidio-analyzer`
and `presidio-anonymizer` modules are required.

```sh
# Download Docker images
docker pull mcr.microsoft.com/presidio-analyzer
docker pull mcr.microsoft.com/presidio-anonymizer

# Run containers with default ports
docker run -d -p 5002:3000 mcr.microsoft.com/presidio-analyzer:latest

docker run -d -p 5001:3000 mcr.microsoft.com/presidio-anonymizer:latest
```

### Customizing the analyzer Docker image for additional languages

The published analyzer image uses the default analyzer configuration, which
loads an English NLP model. To run the analyzer service with additional
languages, build a custom analyzer image with configuration files that declare
the languages, NLP models, and recognizers you want to load.

The analyzer Dockerfile accepts these build arguments:

- `ANALYZER_CONF_FILE`: Analyzer-level settings, including
  `supported_languages`.
- `NLP_CONF_FILE`: NLP engine settings, including spaCy, Stanza, or
  Transformers model names.
- `RECOGNIZER_REGISTRY_CONF_FILE`: Which predefined or custom recognizers to
  load.

For simple deployments you can start from the combined configuration format in
[`default_analyzer_full.yaml`](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/default_analyzer_full.yaml).
For split-file deployments, update the default analyzer, NLP, and recognizer
registry files under
[`presidio-analyzer/presidio_analyzer/conf`](https://github.com/microsoft/presidio/tree/main/presidio-analyzer/presidio_analyzer/conf).

For example, to add Spanish with spaCy:

```yaml
supported_languages:
  - en
  - es

nlp_configuration:
  nlp_engine_name: spacy
  models:
    - lang_code: en
      model_name: en_core_web_lg
    - lang_code: es
      model_name: es_core_news_md

recognizer_registry:
  recognizers:
    - name: SpacyRecognizer
      type: predefined
      supported_languages:
        - en
        - es
    - name: EmailRecognizer
      type: predefined
      supported_languages:
        - en
        - es
```

Save the file inside the analyzer build context, for example as
`presidio-analyzer/presidio_analyzer/conf/custom_analyzer.yaml`, then build the
image and point `ANALYZER_CONF_FILE` at it:

```sh
docker build ./presidio-analyzer \
  -t presidio-analyzer-custom \
  --build-arg ANALYZER_CONF_FILE=presidio_analyzer/conf/custom_analyzer.yaml
```

During the image build, `install_nlp_models.py` installs models referenced by
the configured NLP file or by the `nlp_configuration` section in the analyzer
configuration file. After the image is built, run it as usual:

```sh
docker run -d -p 5002:3000 presidio-analyzer-custom
```

If the image already contains the referenced models, you can also mount
configuration at runtime and set the matching environment variables:

```sh
docker run -d -p 5002:3000 \
  -v "$PWD/custom_analyzer.yaml:/app/custom_analyzer.yaml:ro" \
  -e ANALYZER_CONF_FILE=/app/custom_analyzer.yaml \
  presidio-analyzer-custom
```

Common configuration pitfalls:

- Keep the top-level `supported_languages` value aligned with the recognizer
  registry configuration. The analyzer validates these values when the engine
  starts.
- Include the NLP recognizer for each language that should use model-based NER
  results, such as `SpacyRecognizer`, `StanzaRecognizer`, or
  `TransformersRecognizer`. Warnings such as `NLP recognizer ... is not in the
  list of recognizers for language en` usually mean the NLP engine supports a
  language that the recognizer registry did not enable.
- Build the image with every referenced NLP model installed. Mounting only a new
  YAML file at runtime does not download missing spaCy, Stanza, or Transformers
  models into the container.
- Add languages incrementally and test `/health`, `/recognizers?language=<code>`,
  and `/supportedentities?language=<code>` before adding more models. Large NLP
  model sets can increase image size, startup time, and memory use.

See [Configuring the Analyzer Engine from file](analyzer/analyzer_engine_provider.md),
[Customizing the NLP model](analyzer/customizing_nlp_models.md), and
[Customizing recognizer registry from file](analyzer/recognizer_registry_provider.md)
for the full configuration schema.

### For PII redaction in images

For PII detection in images, the `presidio-image-redactor` is required.

```sh
# Download Docker image
docker pull mcr.microsoft.com/presidio-image-redactor

# Run container with the default port
docker run -d -p 5003:3000 mcr.microsoft.com/presidio-image-redactor:latest
```

Once the services are running, their APIs are available.
API reference and example calls can be found [here](api.md).

## Install from source

To install Presidio from source, first clone the repo:

* using HTTPS

```sh
git clone https://github.com/microsoft/presidio.git
```

* Using SSH

```sh
git clone git@github.com:microsoft/presidio.git
```

Then, build the containers locally.

!!! note "Note"
    Presidio uses [docker-compose](https://docs.docker.com/compose/) to manage the different Presidio containers.

From the root folder of the repo:

```sh
docker-compose up --build
```

Alternatively, you can build and run individual services.
For example, for the `presidio-anonymizer` service:

```sh
docker build ./presidio-anonymizer -t presidio/presidio-anonymizer
```

And run:

```sh
docker run -d -p 5001:5001 presidio/presidio-anonymizer
```

---

For more information on developing locally,
refer to the [setting up a development environment](development.md) section.
