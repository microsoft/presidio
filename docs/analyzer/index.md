# Presidio Analyzer

## Description

The Presidio analyzer is a Python based service for detecting PII entities in text.

During analysis, it runs a set of different *PII Recognizers*,
each one in charge of detecting one or more PII entities using different mechanisms.

Presidio analyzer comes with a set of predefined recognizers,
but can easily be extended with other types of custom recognizers.
Predefined and custom recognizers leverage regex,
Named Entity Recognition and other types of logic to detect PII in unstructured text.

## Table of contents

- [Installation](#installation)
  - [Using pip](#using-pip)
  - [Using Docker](#using-docker)
  - [From source](#from-source)
- [Getting started](#getting-started)
  - [Running in Python](#running-in-python)
  - [Running Presidio as an HTTP server](#running-presidio-as-an-http-server)
    - [Using docker container](#using-docker-container)
    - [Using python runtime](#using-python-runtime)
- [Creating PII recognizers](#creating-pii-recognizers)
- [Outputting the analyzer decision process](#outputting-the-analyzer-decision-process)
- [Supported entities](#supported-entities)
- [API reference](#api-reference)

## Installation

### Using pip

> Consider installing the Presidio python packages on a virtual environment like venv or conda.

To get started with Presidio-analyzer,
download the package and the `en_core_web_lg` spaCy model:

```sh
pip install presidio-analyzer
python -m spacy download en_core_web_lg
```

### Using Docker

> This requires Docker to be installed. [Download Docker](https://docs.docker.com/get-docker/).

```sh
# Download image from Dockerhub
docker pull mcr.microsoft.com/presidio-analyzer

# Run the container with the default port
docker run -d -p 5001:5001 mcr.microsoft.com/presidio-analyzer:latest
```

### From source

First, clone the Presidio repo. [See here for instructions](../installation.md#install-from-source).

Then, build the presidio-analyzer container:

```sh
cd presidio-analyzer
docker build . -t presidio/presidio-analyzer
```

## Getting started

### Running in Python

Once the Presidio-analyzer package is installed, run this simple analysis script:

```python
from presidio_analyzer import AnalyzerEngine

# Set up the engine, loads the NLP module (spaCy model by default) and other PII recognizers
analyzer = AnalyzerEngine()

# Call analyzer to get results
results = analyzer.analyze(text="My phone number is 212-555-5555",
                           entities=["PHONE_NUMBER"],
                           language='en')
print(results)

```

### Running Presidio as an HTTP server

You can run presidio analyzer as an http server using either python runtime or using a docker container.

#### Using docker container

```sh
cd presidio-analyzer
docker run -p 5001:5001 presidio-analyzer 
```

#### Using python runtime

> This requires the Presidio Github repository to be cloned.

```sh
cd presidio-analyzer
python app.py
curl -d '{"text":"John Smith drivers license is AC432223", "language":"en"}' -H "Content-Type: application/json" -X POST http://localhost:3000/analyze
```

## Creating PII recognizers

- [Tutorial on adding new PII recognizers](adding_recognizers.md).
- [Best practices for developing new recognizers](developing_recognizers.md).
- [Multi-language support](languages.md).

## Outputting the analyzer decision process

Presidio analyzer has a built in mechanism for tracing each decision made. This can be useful when attempting to understand a specific PII detection. For more info, see the [decision process](decision_process.md) documentation.

## Supported entities

For a list of supported entities, [click here](../supported_entities.md).

## API reference

`/analyze`

Analyzes a text. Method: `POST`

Parameters

| Name | Type | Optional | Description|
| --- | --- | ---| ---|
| text|string|no|the text to analyze|
| language|string|no|2 characters of the desired language. E.g en, de|
| correlation_id|string|yes|a correlation id to append to headers and traces|
| score_threshold|float|yes|the the minimal score threshold|
| entities|string[]|yes|a list of entities to analyze|
| trace|bool|yes|whether to trace the request|
| remove_interpretability_response|bool|yes|whether to include analysis explanation in the response |

`/recognizers`

Returns a list of supported recognizers.
Method: `GET`

Parameters

| Name | Type | Optional | Description|
| --- | --- | ---| ---|
| language|string|yes|2 characters of the desired language code. e.g., en, de. |

`/supportedentities`

Returns a list of supported entities. Method: `GET`

Parameters

| Name | Type | Optional | Description|
| --- | --- | ---| ---|
| language|string|yes|2 characters of the desired language code. e.g., en, de. |
