# Installing Presidio

## Description

This document describes how to download and install the Presidio services locally.
As Presidio is comprised of several packages/services, this document describes the installation of the entire Presidio suite using `pip` (as Python packages) or using `Docker` (As containerized services).

## Table of contents

- [Download packages using pip](#using-pip)
- [Download and run Docker containers](#using-docker)
- [Install from source](#install-from-source)

## Using pip

> Consider installing the Presidio python packages on a virtual environment like [venv](https://docs.python.org/3/tutorial/venv.html) or [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

### PII anonymization on text

For PII anonymization on text, install the `presidio-analyzer` and `presidio-anonymizer` packages:

```sh
pip install presidio_analyzer
pip install presidio_anonymizer

# Presidio analyzer requires a spaCy language model.
python -m spacy download en_core_web_lg
```

For a more detailed installation of each package, refer to the specific documentation:

- [presidio-analyzer](analyzer/index.md).
- [presidio-anonymizer](anonymizer/index.md).

### PII redaction in images

For PII redaction in images, install the `presidio-image-redactor` package:

```sh
pip install presidio_image_redactor

# Presidio image redactor uses the presidio-analyzer which requires a spaCy language model:
python -m spacy download en_core_web_lg
```

[Click here](image-redactor/index.md) for more information on the presidio-image-redactor package.

## Using Docker

Presidio can expose REST endpoints for each service using Flask and Docker. To download the Presidio Docker containers, run the following command:

> This requires Docker to be installed. [Download Docker](https://docs.docker.com/get-docker/).

### For PII anonymization in text

For PII detection and anonymization in text, the `presidio-analyzer` and `presidio-anonymizer` modules are required.

```sh
# Download images
docker pull mcr.microsoft.com/presidio-analyzer
docker pull mcr.microsoft.com/presidio-anonymizer

# Run containers with default ports
docker run -d -p 5001:5001 mcr.microsoft.com/presidio-analyzer:latest

docker run -d -p 5002:5001 mcr.microsoft.com/presidio-anonymizer:latest
```

### For PII redaction in images

For PII detection in images, the `presidio-image-redactor` is required.

```sh
# Download image
docker pull mcr.microsoft.com/presidio-image-redactor

# Run container with the default port
docker run -d -p 5003:5001 mcr.microsoft.com/presidio-image-redactor:latest
```

Once the services are running, their APIs are available. API reference and example calls can be found [here](api.md).

TODO: Update docs with local build scripts.

## Install from source

To install Presidio from source, first clone the repo:

- using HTTPS

```sh
git clone https://github.com/microsoft/presidio.git
```

- Using SSH

```sh
git clone git@github.com:microsoft/presidio.git
```

Then, build the containers locally.

> Presidio uses [docker-compose](https://docs.docker.com/compose/) to manage the different Presidio containers.

From the root folder of the repo:

```sh
docker-compose --build
```

To run all Presidio services:

```sh
docker-compose up -d
```

Alternatively, you can build and run individual services. For example, for the `presidio-anonymizer` service:

```sh
docker build ./presidio-anonymizer -t presidio/presidio-anonymizer
```

And run:

```sh
docker run -d -p 5002:5001 presidio/presidio-anonymizer
```

For more information on developing locally, refer to the [setting up a development environment](development.md) section.
