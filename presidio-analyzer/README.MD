# Presidio analyzer

## Description

The Presidio analyzer is a Python based service for detecting PII entities in text.

During analysis, it runs a set of different _PII Recognizers_,
each one in charge of detecting one or more PII entities using different mechanisms.

Presidio analyzer comes with a set of predefined recognizers,
but can easily be extended with other types of custom recognizers.
Predefined and custom recognizers leverage regex,
Named Entity Recognition and other types of logic to detect PII in unstructured text.

## Deploy Presidio analyzer to Azure

Use the following button to deploy presidio analyzer to your Azure subscription.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Fpresidio%2Fmain%2Fpresidio-analyzer%2Fdeploytoazure.json)


## Simple usage example

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

## Documentation

-   [Installation](../docs/analyzer/index.md#installation)
    -   [Using pip](../docs/analyzer/index.md#using-pip)
    -   [Using Docker](../docs/analyzer/index.md#using-docker)
    -   [From source](../docs/analyzer/index.md#from-source)
-   [Getting started](../docs/analyzer/index.md#getting-started)
    -   [Running in Python](../docs/analyzer/index.md#running-in-python)
    -   [Running Presidio as an HTTP server](../docs/analyzer/index.md#running-presidio-as-an-http-server)
        -   [Using docker container](../docs/analyzer/index.md#using-docker-container)
        -   [Using python runtime](../docs/analyzer/index.md#using-python-runtime)
-   [Creating PII recognizers](../docs/analyzer/index.md#creating-pii-recognizers)
-   [Outputting the analyzer decision process](../docs/analyzer/index.md#outputting-the-analyzer-decision-process)
-   [API reference](../docs/analyzer/index.md#api-reference)
