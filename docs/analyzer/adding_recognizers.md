# Supporting detection of new types of PII entities

Presidio can be extended to support detection of new types of PII entities, and to support additional languages.

## Introduction to recognizer development

Entity recognizers are Python objects capable of detecting one or more entities in a specific language.
In order to extend Presidio's detection capabilities to new types of PII entities,
these `EntityRecognizer` objects should be added to the existing list of recognizers.

## Types of recognizer classes in Presidio

The following class diagram shows the different types of recognizer families Presidio contains.

![Recognizers class diagram](../assets/recognizers_class_diagram.png)

- The `EntityRecognizer` is an abstract class for all recognizers.
- The `RemoteRecognizer` is an abstract class for calling external PII detectors.
See more info [here](#creating-a-remote-recognizer).
- The abstract class `LocalRecognizer` is implemented by all recognizers running within the Presidio-analyzer process.
- The `PatternRecognizer` is an class for supporting regex and deny-list based recognition logic,
including validation (e.g., with checksum) and context support. See an example [here](#simple-example).

## Extending the analyzer for additional PII entities

1. Create a new class based on `EntityRecognizer`.
2. Add the new recognizer to the recognizer registry so that the `AnalyzerEngine` can use the new recognizer during analysis.

### Simple example

For simple recognizers based on regular expressions or deny-lists,
we can leverage the provided `PatternRecognizer`:

```python
from presidio_analyzer import PatternRecognizer
titles_recognizer = PatternRecognizer(supported_entity="TITLE",
                                      deny_list=["Mr.","Mrs.","Miss"])
```

Calling the recognizer itself:

```python
titles_recognizer.analyze(text="Mr. Schmidt",entities="TITLE")
```

Adding it to the list of recognizers:

```python
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

registry = RecognizerRegistry()
registry.load_predefined_recognizers()

# Add the recognizer to the existing list of recognizers
registry.add_recognizer(titles_recognizer)

# Set up analyzer with our updated recognizer registry
analyzer = AnalyzerEngine(registry=registry)

# Run with input text
text="His name is Mr. Jones"
results = analyzer.analyze(text=text, language="en")
print(results)

```

Alternatively, we can add the recognizer directly to the existing registry:

```python
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()

analyzer.registry.add_recognizer(titles_recognizer)

results = analyzer.analyze(text=text,language="en")
print(results)
```

### Creating a new `EntityRecognizer` in code

To create a new recognizer via code:

1. Create a new Python class which implements [LocalRecognizer](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/local_recognizer.py).
(`LocalRecognizer` implements the base [EntityRecognizer](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/entity_recognizer.py) class)

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
    1. Each recognizer has access to different NLP assets such as tokens, [lemmas](https://en.wikipedia.org/wiki/Lemma_(morphology)), and more.
    These are given through the `nlp_artifacts` parameter.
    Refer to the [source code](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/entity_recognizer.py) for more information.

    2. The `analyze` method should return a list of [RecognizerResult](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/recognizer_result.py).

2. Add it to the recognizer registry using `registry.add_recognizer(my_recognizer)`.

### Creating a remote recognizer

A remote recognizer is an `EntityRecognizer` object interacting with an external service. The external service could be a 3rd party PII detection service or a custom service deployed in parallel to Presidio.

[Sample implementation of a `RemoteRecognizer`](../samples/python/example_remote_recognizer.py).
In this example, an external PII detection service exposes two APIs: `detect` and `supported_entities`. The class implemented here, `ExampleRemoteRecognizer`, uses the `requests` package to call the external service via HTTP.

In this code snippet, we simulate the external PII detector by using the Presidio analyzer. In reality, we would adapt this code to fit the external PII detector we have in hand.

### Creating pre-defined recognizers

Once a recognizer is created, it can either be added to the `RecognizerRegistry` via the `add_recognizer` method, or it could be added into the list of predefined recognizers.
To add a recognizer to the list of pre-defined recognizers:

1. Clone the repo.
2. Create a file containing the new recognizer Python class.
3. Add the recognizer to the `recognizers_map` dict in the `RecognizerRegistry.load_predefined_recognizers` method. In this map, the key is the language the recognizer supports, and the value is the class itself. If your recognizer detects entities in multiple languages, add it to under the "ALL" key.
4. Optional: Update documentation (e.g., the [supported entities list](../supported_entities.md)).

## Azure Text Analytics recognizer 

On how to integrate Presidio with Azure Text Analytics, 
and a sample for a Text Analytics Remote Recognizer, refer to the
[Azure Text Analytics Integration document](../samples/python/text-analytics/index.md).

## PII detection in different languages

For recognizers in new languages, refer to the [languages documentation](languages.md).

## Considerations when creating recognizers

[Best practices for developing PII recognizers](developing_recognizers.md).
