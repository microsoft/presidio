# Presidio anonymizer

## Description

The Presidio anonymizer is a Python based service for anonymizing detected PII text
entities with desired values.

Presidio anonymizer comes by default with the following anonymizers:

- Replace - replaces PII with desired value
- Redact - removes PII completely from text
- Hash - hash the PII using sha256
- FPE - using ff1 algorithm for formatting-Preserving Encryption on the PII
- Mask - mask the selected amount of characters of the PII with a given character

Since text might have several PIIs, the anonymizer handle those scenarios in the
following ways:

- One PII - uses a given or default transformation to anonymize and replace the PII text
  entity.
- Full overlap of PIIs - When one text have several PIIs, the PII with the higher score
  will be taken. Between PIIs with similar scores, the selection will be arbitrary.
- One PII is contained in another - anonymizer will use the PII with larger text.
- Partial intersection - both will be returned concatenated.

## Installation

### As service:

Run presidio_anonymizer/app.py or docker container and use endpoint:

```
POST /anonymize
```

[comment]: <shiranr> (TODO add result example when anonymizer is ready 2626)

```
RESULT
```

```json
{
  "text": "hello world, my name is Jane Doe. My number is: 034453334",
  "transformations": [
    {
      "DEFAULT": {
        "type": "replace",
        "new_value": "val"
      }
    },
    {
      "PHONE_NUMBER": {
        "type": "mask",
        "masking_char": "*",
        "chars_to_mask": 4,
        "from_end": true
      }
    }
  ],
  "analyzer_results": [
    {
      "location": {
        "start": 24,
        "end": 32
      },
      "score": 0.8,
      "field": "NAME",
      "text": "Jane Doe"
    },
    {
      "location": {
        "start": 24,
        "end": 28
      },
      "score": 0.8,
      "field": "FIRST_NAME",
      "text": "Jane"
    },
    {
      "location": {
        "start": 29,
        "end": 32
      },
      "score": 0.6,
      "field": "LAST_NAME",
      "text": "Doe"
    },
    {
      "location": {
        "start": 48,
        "end": 57
      },
      "score": 0.95,
      "field": "PHONE_NUMBER",
      "text": "034453334"
    }
  ]
}
```

Transformation values: replace/redact/hash/mask/fpe Fields values:

### As package:

To get started with Presidio-anonymizer, run the following:

```sh
pip install presidio-anonymizer
```

#### Getting started

[comment]: <shiranr> (TODO need to add when task 2626 - documentation for anonymizer)

```python
from presidio_anonymizer.anonymizer_engine import AnonymizerEngine

engine = AnonymizerEngine()
engine.anonymize()
```
