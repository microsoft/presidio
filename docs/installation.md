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

## Building custom Docker images for additional languages

The official Presidio Docker images only include English (en) language support out of the box.
To add support for additional languages, you need to build a custom Docker image and configure the relevant YAML files.

### Identify which YAML files to modify

The Docker container for `presidio-analyzer` is driven by three configuration files,
passed as build arguments:

| Build argument | Default value | Purpose |
|---|---|---|
| `NLP_CONF_FILE` | `presidio_analyzer/conf/default.yaml` | Defines which NLP engine and model to use |
| `ANALYZER_CONF_FILE` | `presidio_analyzer/conf/default_analyzer.yaml` | Analyzer behavior (thresholds, entity mapping) |
| `RECOGNIZER_REGISTRY_CONF_FILE` | `presidio_analyzer/conf/default_recognizers.yaml` | Which recognizers to load per language |

To add a new language (e.g., German — `de`), you primarily need to modify `default_recognizers.yaml`
to enable recognizers for that language.

### Modify `default_recognizers.yaml`

Open `presidio-analyzer/presidio_analyzer/conf/default_recognizers.yaml`.
For each recognizer you want to enable for your language, add a language entry:

```yaml
- name: SpacyRecognizer
  supported_languages:
  - language: en
  - language: de   # ← add your language here
  type: predefined
```

Not all recognizers support every language. Check the recognizer's source code or the
[supported entities list](../supported_entities.md) for per-language coverage.

### Build the custom Docker image

```sh
docker build \
  --build-arg RECOGNIZER_REGISTRY_CONF_FILE=presidio_analyzer/conf/default_recognizers.yaml \
  --build-arg NLP_CONF_FILE=presidio_analyzer/conf/default.yaml \
  --build-arg ANALYZER_CONF_FILE=presidio_analyzer/conf/default_analyzer.yaml \
  -t my-presidio-analyzer:de \
  ./presidio-analyzer
```

Or, to add multiple languages, modify the YAML files in a local copy and point the build to it:

```sh
cp -r presidio-analyzer presidio-analyzer-custom
# edit presidio-analyzer-custom/presidio_analyzer/conf/default_recognizers.yaml
docker build -t my-presidio-analyzer:multi presidio-analyzer-custom
```

### Add an NLP model for your language (spaCy)

The default NLP engine is spaCy. To support your language, download the corresponding spaCy model
and install it in the Dockerfile. In `presidio-analyzer/install_nlp_models.py`, spaCy models are
installed based on `default.yaml`:

```yaml
# In default.yaml — add your language model:
nlp_engine_name: spacy
models:
  - lang_code: en
    model_name: en_core_web_lg
  - lang_code: de
    model_name: de_core_news_lg
```

Then install the model in your custom Dockerfile (add before the final `COPY . /app/` line):

```dockerfile
RUN python -m spacy download de_core_news_lg
```

### Typical pitfalls

**Adding too many languages at once causes OOM**

Each language model consumes significant RAM/CPU. If you add many large models (e.g., `de_core_news_lg`,
`es_core_news_lg`, `fr_core_news_lg`), the Docker container may run out of memory during model loading.
Start with one language, verify the container starts and responds, then add languages incrementally.

**NLP recognizer warning after adding new languages**

If you see a warning like:

```
UserWarning: NLP recognizer (e.g. SpacyRecognizer, StanzaRecognizer) is not in the list
of recognizers for language en.
```

This means the NLP recognizer is registered for `en` in the `nlp_engine_name` section of `default.yaml`
but not listed in `default_recognizers.yaml` with `language: en`. To fix, ensure the NLP recognizer
has `en` in its `supported_languages` list, or remove `en` from the NLP engine configuration if
you do not need it.

**Memory tuning for production**

For production deployments with multiple language models, consider:

- Setting `WORKERS=1` (default) to limit memory per worker
- Using `--env "PYTHONMALLOCSTATS=1"` to monitor Python memory usage
- Allocating sufficient memory to the Docker daemon (minimum 4 GB recommended for 3+ language models)

### Further reading

- [NLP engine configuration](../analyzer/nlp_engines/spacy_stanza.md)
- [Supported entities list](../supported_entities.md)
- [Development environment setup](development.md)

---

For more information on developing locally,
refer to the [setting up a development environment](development.md) section.