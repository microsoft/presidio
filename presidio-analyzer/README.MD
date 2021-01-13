# Presidio analyzer

## Description
The Presidio analyzer is a Python based service for detecting PII entities in text.

During analysis, it runs a set of different *PII Recognizers*, 
each one in charge of detecting one or more PII entities using different mechanisms.

Presidio analyzer comes with a set of predefined recognizers, 
but can easily be extended with other types of [custom recognizers](#customizing-presidio-analyzer).
Predefined and custom recognizers leverage regex, [spaCy](https://spacy.io/) 
and other types of logic to detect PII in unstructured text.
  
## Installation

To get started with Presidio-analyzer, 
download the package and the `en_core_web_lg` spaCy model, 
preferably in a virtual environment like Conda.


```sh
pip install presidio-analyzer
python -m spacy download en_core_web_sm
```

## Getting started

Here's a simple analysis script:

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

Presidio can be exteded to support new types of PII entities, and to support additional languages.

The three main modules are the `AnalyzerEngine` and the `RecognizerRegistry` and `EntityRecognizer`. 
- The `AnalyzerEngine` is in charge of calling each requested recognizer. 
- The `RecognizerRegistry` is in charge of providing the list of predefined and custom recognizers for analysis.
- The `EntityRecognizer` class can be extended to support new types of PII recognition logic.

### Extending the analyzer for additional PII entities

First, a class based on `EntityRecognizer` needs to be created. 
Second, the new recognizer should be added to the recognizer registry.
So that the `AnalyzerEngine` would be able to use the new recognizer during analysis.

In order to implement a new recognizer by code, follow these two steps:

#### Simple example:

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
    def analyze(self, text, entities, nlp_artifacts):
    ```
    
    Notes:
    1. Each recognizer has access to different NLP assets such as tokens, lemmas, and more. 
    These are given through the `nlp_artifacts` parameter.
    Refer to the [code documentation](presidio_analyzer/entity_recognizer.py) for more information.
    
    2. The `analyze` method should return a list of [RecognizerResult](presidio_analyzer/recognizer_result.py). 

2. Add it to the recognizer registry using `registry.add_recognizer(my_recognizer)`.

### Multi language support

Presidio comes with support for multiple languages, however the basic installations 
contain recognizers focused on English. To extend it to new languages, two main things are required:
1. Replace the NLP model with a model in the desired language
2. Create recognizers capable of detecting PII in the desired language. 
Presidio uses context words surrounding the entity to increase score, so these context words should also be added in the desired language.
