# Presidio analyzer

## Description

The Presidio analyzer is a Python based service for detecting PII entities in text.

During analysis, it runs a set of different *PII Recognizers*,
each one in charge of detecting one or more PII entities using different mechanisms.

Presidio analyzer comes with a set of predefined recognizers,
but can easily be extended with other types of [custom recognizers](#customizing-presidio-analyzer).
Predefined and custom recognizers leverage regex, [spaCy](https://spacy.io/) and other types of logic to detect PII in unstructured text.
  
## Installation

To get started with Presidio-analyzer, download the package and the `en_core_web_lg` spaCy model, preferably in a virtual environment like Conda.

```sh
pip install presidio-analyzer
python -m spacy download en_core_web_lg
```

## Getting started

### Running Presidio as an HTTP server

You can run presidio analyzer as an http server using either python runtime or using a docker container.

#### Using python runtime

```sh
cd presidio-analyzer
python app.py
curl -d '{"text":"John Smith drivers license is AC432223", "language":"en"}' -H "Content-Type: application/json" -X POST http://localhost:3000/analyze
```

#### Using docker container

```sh
cd presidio-analyzer
docker build -t presidio-analyzer --build-arg NAME=presidio-analyzer .
docker run -p 5001:5001 presidio-analyzer 
```

Note: you can change the spacy model which is downloaded to the container at build time, using the following build command:

```sh
docker build -t presidio-analyzer --build-arg NAME=presidio-analyzer  --build-arg SPACY_MODEL=en_core_web_sm .
```

TODO: The Analyzer container is built with a single spacy model. Add support for multiple models will worked on in user story #2678

### Simple analysis script

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

## Customizing Presidio analyzer

Presidio can be extended to support new types of PII entities, and to support additional languages.

The three main modules are the `AnalyzerEngine` and the `RecognizerRegistry` and `EntityRecognizer`.

- The `AnalyzerEngine` is in charge of calling each requested recognizer.
- The `RecognizerRegistry` is in charge of providing the list of predefined and custom recognizers for analysis.
- The `EntityRecognizer` class can be extended to support new types of PII recognition logic.

### Extending the analyzer for additional PII entities

First, a class based on `EntityRecognizer` needs to be created.
Second, the new recognizer should be added to the recognizer registry.
So that the `AnalyzerEngine` would be able to use the new recognizer during analysis.

In order to implement a new recognizer by code, follow these two steps:

#### Simple example

For simple recognizers based on regular expressions or deny-lists,
we can leverage the provided `PatternsRecognizer`:

```python
from presidio_analyzer import PatternRecognizer
titles_recognizer = PatternRecognizer(supported_entity="TITLE",
                                      deny_list=["Mr.","Mrs.","Miss"])
```

Calling the recognizer itself:

```python
titles_recognizer.analyze(text="Mr. Schmidt",entities="TITLE")
```

Adding to the list of recognizers:

```python
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

text="His name is Mr. Jones"

registry = RecognizerRegistry()
registry.load_predefined_recognizers()

# Add new recognizer
registry.add_recognizer(titles_recognizer)

# Set up analyzer with our updated recognizer registry
analyzer = AnalyzerEngine(registry=registry)

results = analyzer.analyze(text=text,language="en")
print(results)

```

Alternatively, we can add the recognizer to the existing analyzer:

```python
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()

analyzer.registry.add_recognizer(titles_recognizer)

results = analyzer.analyze(text=text,language="en")
print(results)
```

#### Creating a new `EntityRecognizer` in code

There are various types of Recognizers in Presidio:

- `EntityRecognizer`, the base class
- `PatternsRecognizer`, for regex and deny-list based detection
- `LocalRecognizer`: A base class for all recognizers living within the same process as the `AnalyzerEngine`.
- `RemoteRecognizer`: A base class for accessing external recognizers,
such as 3rd party services or ML models served outside the main Presidio Python process.

To create a new recognizer via code:

1. Create a new Python class which implements [LocalRecognizer](presidio_analyzer/local_recognizer.py).
(`LocalRecognizer` implements the base [EntityRecognizer](presidio_analyzer/entity_recognizer.py) class.)

    This class has the following functions:

    i. load: load a model / resource to be used during recognition

    ```python
   def load(self)
    ```

    ii. analyze: The main function to be called for getting entities out of the new recognizer:

    ```python
   def analyze(self, text, entities, nlp_artifacts)
    ```

    Notes:
    1. Each recognizer has access to different NLP assets such as tokens, lemmas, and more.
    These are given through the `nlp_artifacts` parameter.
    Refer to the [code documentation](presidio_analyzer/entity_recognizer.py) for more information.

    2. The `analyze` method should return a list of [RecognizerResult](presidio_analyzer/recognizer_result.py).

2. Add it to the recognizer registry using `registry.add_recognizer(my_recognizer)`.

### Multi language support

Presidio can detect PII in multiple languages. In its default configuration,
it contains recognizers and models for English.
To allow Presidio to support additional languages, these modules needs to be configured:

1. The NlpEngine which contains the NLP model which performs tokenization,
lemmatization, Named Entity Recognition and other NLP tasks.
2. PII recognizers should be adapted or created.

#### Configuring the NLP Engine

As its internal NLP engine, Presidio supports both [spaCy](https://spacy.io/usage/models)
and [Stanza](https://github.com/stanfordnlp/stanza). To set up new models, follow these two steps:

1. Download the spaCy/Stanza NER models for your desired language.
   To download a new model with spaCy:

   ```shell script
   python -m spacy download es_core_news_md
   ```

   In this example we download the medium size model for Spanish.

   To download a new model with Stanza:

   ```python
   import stanza
   stanza.download("en") # where en is the language code of the model.
   ```

   For the available models, follow these links: [spaCy](https://spacy.io/usage/models), [stanza](https://stanfordnlp.github.io/stanza/available_models.html#available-ner-models).
2. Update the models configuration
    - **Via configuration**: Add the downloaded models to the [default `conf` file](conf/default.yaml).

        An example Conf file:

        ```yaml
        nlp_engine_name: spacy
        models:
            -
            lang_code: en
            model_name: en_core_web_lg
            -
            lang_code: es
            model_name: es_core_news_md 
        ```

        In this configuration we use the `en_core_web_lg` spaCy model for English, and `es_core_news_md` spaCy model for Spanish.

    - **Via code**: Create an `NlpEngine` using the `create_nlp_engine` method and a configuration dict:

        ```python
        from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
        from presidio_analyzer.nlp_engine import create_nlp_engine

        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "es", "model_name": "es_core_news_md"},
                       {"lang_code": "en", "model_name": "en_core_web_lg"}],
        }

        nlp_engine = create_nlp_engine(nlp_configuration=configuration)
        analyzer_engine = AnalyzerEngine(
            nlp_engine=nlp_engine, supported_languages=["en", "es"]
        )
        results_spanish = analyzer_engine.analyze(text="Mi nombre es David", language="es")
        print(results_spanish)

        results_english = analyzer_engine.analyze(text="My name is David", language="en")
        print(results_english)
        ```

#### Set up language specific recognizers

Recognizers are language dependent either by their logic or by the context words used while scanning the surrounding of a detected entity.
As these context words are used to increase score, they should be in the expected input language. Consider updating the context words of existing recogniers or add new recognizers to support new languages.

## HTTP API

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
