# Presidio analyzer

## Description
The presidio-analyzer is a Python based service which does the actual detection of PII entities.

The main modules in presidio-analyzer are the AnalyzerEngine and the RecognizerRegistry. The AnalyzerEngine is in charge of calling each requested recognizer. the RecognizerRegistry is in charge of providing the list of predefined and custom recognizers for analysis.

## Extending the analyzer for additional PII entities by introducing new code-based recognizers

Code based recognizers are written in Python and are a part of the presidio-analyzer module.
The main modules in `presidio-analyzer` are the `AnalyzerEngine` and the `RecognizerRegistry`.
The `AnalyzerEngine` is in charge of calling each requested recognizer.
The `RecognizerRegistry` is in charge of providing the list of predefined and custom recognizers for analysis.

In order to implement a new recognizer by code, follow these two steps:

a. Implement the abstract recognizer class:

Create a new Python class which implements [LocalRecognizer](presidio_analyzer/local_recognizer.py).
`LocalRecognizer` implements the base [EntityRecognizer](presidio_analyzer/entity_recognizer.py) class.
All local recognizers run locally together with all other predefined recognizers as a part of the `presidio-analyzer` Python process. In contrast, `RemoteRecognizer` is an abstract class for recognizers that are external to the `presidio-analyzer` service, for example on a different microservice.

The `EntityRecognizer` abstract class requires the implementation the following methods:

i. initializing a model. Occurs when the `presidio-analyzer` process starts:

```python
def load(self)
```

ii. analyze: The main function to be called for getting entities out of the new recognizer:

```python
def analyze(self, text, entities, nlp_artifacts):
```

The `analyze` method should return a list of [RecognizerResult](presidio_analyzer/recognizer_result.py). Refer to the [code documentation](presidio_analyzer/entity_recognizer.py) for more information.

b. Reference and add the new class to the `RecognizerRegistry` module, in the `load_predefined_recognizers` method, which registers all code based recognizers.
