# Interpretability Traces

## Background
Presidio offers interpretability traces, which allows you to investigate a specific api request, by exposing a `correlation-id` as part of the api response headers.

The interpretability traces explain why a specific PII was detected. For example: which recognizer detected the entity, which regex / ML model were used, which context words improved the score, etc.

## How it works
The current implementation of the `App Tracer` class writes the traces into the `stdout`. This can be easily customized to have your traces written to different destination of your choice. 

Each trace contains a `correlation-id` which correlates to a specific api request. The api returns a `x-correlation-id` header which you can use to the `correlation-id` and query the `stdout` logs.

By having the traces written into the `stdout` it's very easy to configure a monitoring solution to ease the process of reading processing the tracing logs in a distributed system. Read our [monitoring guide](monitoring_logging.md) for more information.

## Examples
For the a request with the following text:
``` 
My name is Bart Simpson, my Credit card is: 4095-2609-9393-4932,  my phone is 425 8829090 
```

The following traces will be written:
```
[2019-07-14 14:22:32,409][InterpretabilityMock][INFO][00000000-0000-0000-0000-000000000000][nlp artifacts:{'entities': (Bart Simpson, 4095, 425), 'tokens': ['My', 'name', 'is', 'Bart', 'Simpson', ',', 'my', 'Credit', 'card', 'is', ':', '4095', '-', '2609', '-', '9393', '-', '4932', ',', ' ', 'my', 'phone', 'is', '425', '8829090'], 'lemmas': ['My', 'name', 'be', 'Bart', 'Simpson', ',', 'my', 'Credit', 'card', 'be', ':', '4095', '-', '2609', '-', '9393', '-', '4932', ',', ' ', 'my', 'phone', 'be', '425', '8829090'], 'tokens_indices': [0, 3, 8, 11, 16, 23, 25, 28, 35, 40, 42, 44, 48, 49, 53, 54, 58, 59, 63, 65, 66, 69, 75, 78, 82], 'keywords': ['bart', 'simpson', 'credit', 'card', '4095', '2609', '9393', '4932', ' ', 'phone', '425', '8829090']}]

[2019-07-14 14:22:32,417][InterpretabilityMock][INFO][00000000-0000-0000-0000-000000000000][["{'entity_type': 'CREDIT_CARD', 'start': 44, 'end': 63, 'score': 1.0, 'analysis_explanation': {'recognizer': 'CreditCardRecognizer', 'pattern_name': 'All Credit Cards (weak)', 'pattern': '\\\\b((4\\\\d{3})|(5[0-5]\\\\d{2})|(6\\\\d{3})|(1\\\\d{3})|(3\\\\d{3}))[- ]?(\\\\d{3,4})[- ]?(\\\\d{3,4})[- ]?(\\\\d{3,5})\\\\b', 'original_score': 0.3, 'score': 1.0, 'textual_explanation': None, 'score_context_improvement': 0.7, 'supportive_context_word': 'credit', 'validation_result': True}}", "{'entity_type': 'PERSON', 'start': 11, 'end': 23, 'score': 0.85, 'analysis_explanation': {'recognizer': 'SpacyRecognizer', 'pattern_name': None, 'pattern': None, 'original_score': 0.85, 'score': 0.85, 'textual_explanation': \"Identified as PERSON by Spacy's Named Entity Recognition\", 'score_context_improvement': 0, 'supportive_context_word': '', 'validation_result': None}}", "{'entity_type': 'PHONE_NUMBER', 'start': 78, 'end': 89, 'score': 0.85, 'analysis_explanation': {'recognizer': 'UsPhoneRecognizer', 'pattern_name': 'Phone (medium)', 'pattern': '\\\\b(\\\\d{3}[-\\\\.\\\\s]\\\\d{3}[-\\\\.\\\\s]??\\\\d{4})\\\\b', 'original_score': 0.5, 'score': 0.85, 'textual_explanation': None, 'score_context_improvement': 0.35, 'supportive_context_word': 'phone', 'validation_result': None}}"]]
```

The format of the traces is: `[Date Time][Interpretability][Log Level][Unique Correlation ID][Trace Message]`

## Custom traces
Currently the traces are written automatically. It means that when you add a new recognizer, a generic interpretability traces will be written.

However, it's possible to write custom data to the traces if you wish to.

For exmple, the [spacy_recognizer.py](https://github.com/microsoft/presidio/blob/master/presidio-analyzer/presidio_analyzer/predefined_recognizers/spacy_recognizer.py) implemented a custom trace as follows:
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
Interpretability traces are enabled by default. Disable App Tracing by setting the `enabled` constructor parameter to `False`.
PII entities are not stored in the Traces by default. Enable it by either set an evironment variable `ENABLE_TRACE_PII` to `True`, or you can set it directly in the command line, using the `enable-trace-pii` argument as follows:
```bash
pipenv run python app.py serve --grpc-port 3001 --enable-trace-pii True
```

## Notes
* Interpretability traces explain why PIIs were detected, but not why they were not detected.
