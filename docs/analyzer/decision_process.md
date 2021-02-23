# The Presidio-analyzer decision process

## Background

Presidio-analyzer traces its decision process, which allows you to investigate a specific api request, by exposing a `correlation-id` as part of the api response headers.

The decision process traces explain why a specific PII was detected. For example: Which recognizer detected the entity, which regex / ML model were used, which context words improved the score, etc.

## How it works

The decision process can either be returned together with the Presidio-analyzer `/analyze` response, or logged into a dedicated logger.

### Getting the decision process as part of the response

The decision process result is added to the response automatically.
To enable/disable it, call the `analyze` method with `remove_interpretability_response` as False and True, respectively.

### Logging the decision process

Each api request contains a `correlation-id` which is the trace identification. It will help you to query the stdout logs.
The id can be retrieved from each API response header: `x-correlation-id`.

By having the traces written into the `stdout` it's very easy to configure a monitoring solution to ease the process of reading processing the tracing logs in a distributed system.

## Examples

For the a request with the following text:

```text
My name is Bart Simpson, my Credit card is: 4095-2609-9393-4932,  my phone is 425 8829090 
```

The following traces will be written to log, with this format: 

`[Date Time][decision_process][Log Level][Unique Correlation ID][Trace Message]`

```text
[2019-07-14 14:22:32,409][decision_process][INFO][00000000-0000-0000-0000-000000000000][nlp artifacts:{'entities': (Bart Simpson, 4095, 425), 'tokens': ['My', 'name', 'is', 'Bart', 'Simpson', ',', 'my', 'Credit', 'card', 'is', ':', '4095', '-', '2609', '-', '9393', '-', '4932', ',', ' ', 'my', 'phone', 'is', '425', '8829090'], 'lemmas': ['My', 'name', 'be', 'Bart', 'Simpson', ',', 'my', 'Credit', 'card', 'be', ':', '4095', '-', '2609', '-', '9393', '-', '4932', ',', ' ', 'my', 'phone', 'be', '425', '8829090'], 'tokens_indices': [0, 3, 8, 11, 16, 23, 25, 28, 35, 40, 42, 44, 48, 49, 53, 54, 58, 59, 63, 65, 66, 69, 75, 78, 82], 'keywords': ['bart', 'simpson', 'credit', 'card', '4095', '2609', '9393', '4932', ' ', 'phone', '425', '8829090']}]

[2019-07-14 14:22:32,417][decision_process][INFO][00000000-0000-0000-0000-000000000000][["{'entity_type': 'CREDIT_CARD', 'start': 44, 'end': 63, 'score': 1.0, 'analysis_explanation': {'recognizer': 'CreditCardRecognizer', 'pattern_name': 'All Credit Cards (weak)', 'pattern': '\\\\b((4\\\\d{3})|(5[0-5]\\\\d{2})|(6\\\\d{3})|(1\\\\d{3})|(3\\\\d{3}))[- ]?(\\\\d{3,4})[- ]?(\\\\d{3,4})[- ]?(\\\\d{3,5})\\\\b', 'original_score': 0.3, 'score': 1.0, 'textual_explanation': None, 'score_context_improvement': 0.7, 'supportive_context_word': 'credit', 'validation_result': True}}", "{'entity_type': 'PERSON', 'start': 11, 'end': 23, 'score': 0.85, 'analysis_explanation': {'recognizer': 'SpacyRecognizer', 'pattern_name': None, 'pattern': None, 'original_score': 0.85, 'score': 0.85, 'textual_explanation': \"Identified as PERSON by Spacy's Named Entity Recognition\", 'score_context_improvement': 0, 'supportive_context_word': '', 'validation_result': None}}", "{'entity_type': 'PHONE_NUMBER', 'start': 78, 'end': 89, 'score': 0.85, 'analysis_explanation': {'recognizer': 'UsPhoneRecognizer', 'pattern_name': 'Phone (medium)', 'pattern': '\\\\b(\\\\d{3}[-\\\\.\\\\s]\\\\d{3}[-\\\\.\\\\s]??\\\\d{4})\\\\b', 'original_score': 0.5, 'score': 0.85, 'textual_explanation': None, 'score_context_improvement': 0.35, 'supportive_context_word': 'phone', 'validation_result': None}}"]]
```

## Writing custom decision process for a recognizer

When setting up the AnalyzerEngine with `enable_trace_pii=True`, the traces are written automatically. It means that when you add a new recognizer, a generic decision process trace will be written.

However, it's possible to append custom information to the decision process if you wish to.

For example, the [spacy_recognizer.py](https://github.com/microsoft/presidio/blob/master/presidio-analyzer/presidio_analyzer/predefined_recognizers/spacy_recognizer.py) implements a custom trace as follows:

```python
SPACY_DEFAULT_EXPLANATION = "Identified as {} by Spacy's Named Entity Recognition"

def build_spacy_explanation(recognizer_name, original_score, entity):
    explanation = AnalysisExplanation(
        recognizer=recognizer_name,
        original_score=original_score,
        textual_explanation=SPACY_DEFAULT_EXPLANATION.format(entity))
    return explanation
```

The `textual_explanation` field in `AnalysisExplanation` class allows you to add your own custom text into the final trace which will be written.

## Enabling/Disabling Traces

Decision-process traces are controlled by the `enable_trace_pii` parameter.

```python
from presidio_analyzer import AnalyzerEngine

# Set up the engine, loads the NLP module (spaCy model by default) and other PII recognizers
analyzer = AnalyzerEngine(enable_trace_pii=True)

# Call analyzer to get results
results = analyzer.analyze(text="My phone number is 212-555-5555",
                           entities=["PHONE_NUMBER"],
                           language='en')
print(results)
```

!!! note "Note" 
    These traces leverage the Python `logging` mechanisms. In the default configuration, A `StreamHandler` is used to write these logs to `sys.stdout`.

!!! warning "Warning"
    Decision-process traces explain why PIIs were detected, 
    but not why they were not detected!
