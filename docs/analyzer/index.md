# Presidio Analyzer

The Presidio analyzer is a Python based service for detecting PII entities in text.

During analysis, it runs a set of different _PII Recognizers_,
each one in charge of detecting one or more PII entities using different mechanisms.

Presidio analyzer comes with a set of predefined recognizers,
but can easily be extended with other types of custom recognizers.
Predefined and custom recognizers leverage regex,
Named Entity Recognition and other types of logic to detect PII in unstructured text.

![Analyzer Design](../assets/analyzer-design.png)

## Installation

see [Installing Presidio](../installation.md).

## Getting started

=== "Python"

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

=== "As an HTTP server"

    You can run presidio analyzer as an http server using either python runtime or using a docker container.

    #### Using docker container

    ```sh
    cd presidio-analyzer
    docker run -p 5002:3000 presidio-analyzer
    ```

    #### Using python runtime

    !!! note "Note"
        This requires the Presidio Github repository to be cloned.

    ```sh
    cd presidio-analyzer
    python app.py
    curl -d '{"text":"John Smith drivers license is AC432223", "language":"en"}' -H "Content-Type: application/json" -X POST http://localhost:3000/analyze
    ```

## Creating PII recognizers

Presidio analyzer can be easily extended to support additional PII entities.
See [this tutorial on adding new PII recognizers](adding_recognizers.md)
for more information.

## Multi-language support

Presidio can be used to detect PII entities in multiple languages.
Refer to the [multi-language support](languages.md) for more information.

## Outputting the analyzer decision process

Presidio analyzer has a built in mechanism for tracing each decision made. This can be useful when attempting to understand a specific PII detection. For more info, see the [decision process](decision_process.md) documentation.

## Supported entities

For a list of the current supported entities:
[Supported entities](../supported_entities.md).

## API reference

Follow the [API Spec](https://microsoft.github.io/presidio/api-docs/api-docs.html#tag/Analyzer) for the Analyzer REST API reference details and [Analyzer Python API](../api/analyzer_python.md) for Python API reference

## Samples

Samples illustrating the usage of the Presidio Analyzer can be found in the [Python samples](../samples/).
