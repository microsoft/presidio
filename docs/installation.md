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

#### Building a custom `presidio-analyzer` image

The published analyzer image ships with the default English-only YAML files:

- `presidio_analyzer/conf/default_analyzer.yaml`
- `presidio_analyzer/conf/default.yaml`
- `presidio_analyzer/conf/default_recognizers.yaml`

From the repository root (after cloning this repo), run the following commands to add
more languages or enable a different recognizer mix. Create custom copies of those
files inside the `presidio-analyzer/` build context and point the Docker build to
them with build arguments.

For example:

```sh
cp presidio-analyzer/presidio_analyzer/conf/default_analyzer.yaml \
  presidio-analyzer/presidio_analyzer/conf/custom_analyzer.yaml
cp presidio-analyzer/presidio_analyzer/conf/default.yaml \
  presidio-analyzer/presidio_analyzer/conf/custom_nlp.yaml
cp presidio-analyzer/presidio_analyzer/conf/default_recognizers.yaml \
  presidio-analyzer/presidio_analyzer/conf/custom_recognizers.yaml
```

Then update the copies as needed:

- Add every runtime language to `supported_languages` in both
  `custom_analyzer.yaml` and `custom_recognizers.yaml`.
- Configure the NLP models for those languages in `custom_nlp.yaml`.
- Enable or add recognizers that should run for the new languages.

Build the image with the custom file paths:

```sh
docker build ./presidio-analyzer \
  -t myorg/presidio-analyzer-custom \
  --build-arg ANALYZER_CONF_FILE=presidio_analyzer/conf/custom_analyzer.yaml \
  --build-arg NLP_CONF_FILE=presidio_analyzer/conf/custom_nlp.yaml \
  --build-arg RECOGNIZER_REGISTRY_CONF_FILE=presidio_analyzer/conf/custom_recognizers.yaml
```

Run it the same way as the default image:

```sh
docker run -d -p 5002:3000 myorg/presidio-analyzer-custom
```

!!! note "Important configuration checks"

    - `supported_languages` must match between the analyzer and recognizer-registry YAML files.
    - The Docker build installs the NLP models declared in `NLP_CONF_FILE` (or in the analyzer file if you use a single combined config), so adding more or larger models increases build time and image size.
    - If the container logs warnings such as `NLP recognizer ... is not in the list of recognizers for language ...`, check that the recognizer registry still includes the NLP recognizer for that language (for example `SpacyRecognizer`) and that the same language code appears in both YAML files.
    - If you are experimenting with many languages at once, start with a smaller subset first. Downloading and loading several large NLP models in one image can significantly increase memory usage during build and startup.

For more background on the YAML structure, see:

- [Analyzer Engine Provider](analyzer/analyzer_engine_provider.md)
- [PII detection in different languages](analyzer/languages.md)
- [Customizing NLP models](analyzer/customizing_nlp_models.md)
- [Recognizer registry configuration](analyzer/recognizer_registry_provider.md)

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
