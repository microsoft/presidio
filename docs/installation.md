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

---

## Building Custom Docker Images

This section provides detailed instructions for building custom Docker images to support additional languages and custom configurations.

### Overview

The official Presidio Docker images support English by default. To add support for additional languages, you'll need to build custom images using the provided YAML configuration files.

### Key Configuration Files

The main configuration files for customizing Presidio are located in the root directory:

- `docker-compose.yml` - Main compose file
- `docker-compose-image.yml` - Image-specific configuration
- `docker-compose-text.yml` - Text processing configuration
- `docker-compose-transformers.yml` - Transformer models configuration

### Adding Support for Additional Languages

#### Step 1: Modify the NLP Configuration

The primary way to add language support is through the `NER_REGOGNIZERS` environment variable. Create a custom Dockerfile:

```dockerfile
FROM mcr.microsoft.com/presidio-analyzer:latest

# Install additional language models
RUN python -m spacy download es_core_news_lg
RUN python -m spacy download fr_core_news_lg
RUN python -m spacy download de_core_news_lg

# Set environment variables for additional languages
ENV NER_RECOGNIZERS='{"en": ["SpacyRecognizer"], "es": ["SpacyRecognizer"], "fr": ["SpacyRecognizer"], "de": ["SpacyRecognizer"]}'
ENV DEFAULT_LANGUAGES="en,es,fr,de"

CMD ["python", "-m", "presidio-analyzer"]
```

#### Step 2: Build Your Custom Image

```bash
docker build -t my-presidio-analyzer:custom -f Dockerfile .
```

#### Step 3: Run with Custom Configuration

```bash
docker run -d -p 5002:3000 \
  -e NER_RECOGNIZERS='{"en": ["SpacyRecognizer"], "es": ["SpacyRecognizer"]}' \
  -e DEFAULT_LANGUAGES="en,es" \
  my-presidio-analyzer:custom
```

### Typical Pitfalls to Avoid

#### Memory Issues with Multiple Languages

!!! warning "Important"

    Adding 10+ languages at once may cause the Docker image to run out of memory during model loading.

**Solution:** Add languages incrementally and optimize model sizes:

```dockerfile
# Use smaller models when possible
RUN python -m spacy download es_core_web_sm  # Use small model
# Instead of: RUN python -m spacy download es_core_web_lg  # Large model
```

Alternatively, use lazy loading for NLP models.

#### NLP Recognizer Warnings

If you see warnings like:
```
UserWarning: NLP recognizer (e.g. SpacyRecognizer, StanzaRecognizer) is not in the list of recognizers for language en.
```

**Solution:** Ensure your recognizers are properly registered in the `NER_RECOGNIZERS` configuration:

```bash
docker run -d -p 5002:3000 \
  -e NER_RECOGNIZERS='{"en": ["SpacyRecognizer"], "es": ["SpacyRecognizer"]}' \
  my-presidio-analyzer:custom
```

### Complete Example: Multi-Language Support

Create a `Dockerfile.multilang`:

```dockerfile
FROM mcr.microsoft.com/presidio-analyzer:latest

# Install Spanish, French, German, and Italian models
RUN python -m spacy download es_core_web_sm && \
    python -m spacy download fr_core_web_sm && \
    python -m spacy download de_core_web_sm && \
    python -m spacy download it_core_web_sm

# Configure recognizers for all supported languages
ENV NER_RECOGNIZERS='{
  "en": ["SpacyRecognizer"],
  "es": ["SpacyRecognizer"],
  "fr": ["SpacyRecognizer"],
  "de": ["SpacyRecognizer"],
  "it": ["SpacyRecognizer"]
}'
ENV DEFAULT_LANGUAGES="en,es,fr,de,it"

EXPOSE 3000

CMD ["python", "-m", "presidio-analyzer"]
```

Build and run:

```bash
docker build -f Dockerfile.multilang -t presidio-multilang:latest .
docker run -d -p 5002:3000 presidio-multilang:latest
```

### Using Custom YAML Files

For more complex configurations, you can modify the existing YAML files:

1. **Edit `docker-compose-text.yml`** to customize text processing
2. **Edit `docker-compose-transformers.yml`** to add custom transformer models
3. **Build with custom compose:**

```bash
docker-compose -f docker-compose-text.yml build
docker-compose -f docker-compose-text.yml up
```

### Troubleshooting

#### Container Out of Memory

If your container runs out of memory:
- Reduce the number of languages loaded simultaneously
- Use smaller spaCy models (`_sm` instead of `_lg`)
- Limit the number of NLP engine workers

#### Model Not Found

If you get "model not found" errors:
- Ensure the model is properly installed in the Dockerfile
- Verify the model name matches exactly (case-sensitive)
- Check that the model supports the requested language

---

For more information on developing locally,
refer to the [setting up a development environment](development.md) section.
