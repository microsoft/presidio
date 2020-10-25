# Using the Analyzer Service

Throughout this tutorial, we’ll walk you through the creation of a basic request to the analyzer and anonymizer components.

See [Install Presidio](deploy.md) for a tutorial on how to install Presidio.

## Analyze your textual data

Analysis could be performed either by using Presidio as a deployed service (Method 1), or using the `presidio-analyzer` python package (Method 2).

### Method 1

First, we need to serve our model. We can do that very easily with (Takes about 10 seconds to load)

```sh
./presidio-analyzer serve
```

Now that our model is up and running, we can send PII text to it.

_From another shell_

```sh
./presidio-analyzer analyze --text "John Smith drivers license is AC432223" --fields "PERSON" "US_DRIVER_LICENSE"
```

The expected result is:

```json
{
  "analyzeResults": [
    {
      "text": "John Smith",
      "field": {
        "name": "PERSON"
      },
      "score": 0.8500000238418579,
      "location": {
        "end": 10,
        "length": 10,
        "start": 0
      }
    },
    {
      "text": "AC432223",
      "field": {
        "name": "US_DRIVER_LICENSE"
      },
      "score": 0.6499999761581421,
      "location": {
        "start": 30,
        "end": 38,
        "length": 8
      }
    }
  ]
}
```

### Method 2

Use the analyzer Python code by importing `analyzer_engine.py` from `presidio-analyzer/presidio_analyzer`

```python
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
results = analyzer.analyze(text="My phone number is 212-555-5555",
                           entities=["PHONE_NUMBER"],
                           language='en',
                           all_fields=False)
print(results)
```

## Using multiple languages

### Option 1: Configure which spacy/stanza models to load

First, we need to edit the configuration file (i.e. [/presidio-analyzer/conf/spacy_multilingual.yaml](../presidio-analyzer/presidio/conf/spacy_multilingual.yaml) ) to specify what languages to load. Like this:

```spacy_multilingual.yaml
nlp_engine_name: spacy
models:
  -
    lang_code: en
    model_name: en_core_web_lg
  -
    lang_code: es
    model_name: es_core_news_md
```

In this configuration we use the `en_core_web_lg` spaCy model for English, and `es_core_news_md` spaCy model for Spanish. Presidio supports both [spaCy](https://spacy.io/usage/models) and [Stanza](https://github.com/stanfordnlp/stanza) models.

NOTE: make sure that you have all your spacy models downloaded with a command like this:

```bash
python3 -m spacy download es_core_news_md
```

Then, we need to serve our models as showed before in Method 1.

Now that our models is up and running, we can send PII text to it.

_From another shell_

You can make an English language query like before or use Spanish language query like this:

```sh
./presidio-analyzer analyze --text "Mi nombre es Francisco Pérez con DNI 55555555-K, vivo en Madrid y trabajo para la ONU." --fields "ES_NIF" "LOCATION" "PERSON" --language "es"
````

The expected result is:

```json
{
  "analyzeResults": [
    {
      "field": {
        "name": "ES_NIF"
      },
      "score": 1.0,
      "location": {
        "start": 37,
        "end": 47,
        "length": 10
      }
    },
    {
      "field": {
        "name": "PERSON"
      },
      "score": 0.8500000238418579,
      "location": {
        "start": 13,
        "end": 28,
        "length": 15
      }
    },
    {
      "field": {
        "name": "LOCATION"
      },
      "score": 0.8500000238418579,
      "location": {
        "start": 57,
        "end": 63,
        "length": 6
      }
    }
  ],
  "requestId": "d89ffd66-2adf-486f-a040-4e4f80af7a86"
}
```

### Option 2: load models programmatically

Use the analyzer Python code by importing `analyzer_engine.py`, `SpacyNlpEngine` and `RecognizerRegistry`

```python
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_analyzer.recognizer_registry import RecognizerRegistry

registry = RecognizerRegistry()
nlp = SpacyNlpEngine({"en": "en_core_web_lg", "es": "es_core_news_md"})
registry.load_predefined_recognizers(["en", "es"], "spacy")
analyzer = AnalyzerEngine(registry=registry, nlp_engine=nlp, default_language="es")

# English query with just one entity
results = analyzer.analyze(text="My phone number is 212-555-5555",
                           entities=["PHONE_NUMBER"],
                           language='en',
                           all_fields=False)

print(results)

# Spanish query with all entities and score_threshold
results = analyzer.analyze(text = "Mi nombre es Francisco Pérez con DNI 55555555-K, \
                         vivo en Madrid y trabajo para la ONU.",
                         entities=[],
                         language='es',
                         all_fields=True,
                         score_threshold=0.5)
print(results)
```
