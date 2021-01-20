# Presidio anonymizer

## Description

The Presidio anonymizer is a Python based module for anonymizing detected PII text
entities with desired values.

Presidio anonymizer comes by default with the following anonymizers:

- Replace - replaces PII with desired value
- Redact - removes PII completely from text
- Hash - hash the PII using sha256
- FPE - using ff1 algorithm for formatting-Preserving Encryption on the PII
- Mask - mask the selected amount of characters of the PII with a given character

[comment]: <shiranr> (#TODO need to fill this once the the functionality is done 2656 - 2659)
Each anonymizer requires different values:

- Replace -
- Redact - None
- Hash - None
- FPE -
- Mask -

As the input text could potentially have overlapping PII entities, there are different
anonymization scenarios:

- No overlap (single PII) - single PII over text entity, uses a given or default
  transformation to anonymize and replace the PII text entity.
- Full overlap of PIIs - When one text have several PIIs, the PII with the higher score
  will be taken. Between PIIs with identical scores, the selection will be arbitrary.
- One PII is contained in another - anonymizer will use the PII with larger text.
- Partial intersection - both will be returned concatenated.

Example of how each scenario would work. Our text will be:

My name is Inigo Montoya. You Killed my Father. Prepare to die. BTW my number is:
03-232323.

- No overlaps - only Inigo was recognized as NAME:
  My name is <NAME> Montoya. You Killed my Father. Prepare to die. BTW my number is:
  03-232323.
- Full overlap - the number was recognized as PHONE_NUMBER with score of 0.7 and as SSN
  with score of 0.6, we will take the higher score:
  My name is Inigo Montoya. You Killed my Father. Prepare to die. BTW my number is: <
  PHONE_NUMBER>
- One PII is contained is another - Inigo was recognized as FIRST_NAME and Inigo Montoya
  was recognized as NAME, we will take the larger one:
  My name is <NAME>. You Killed my Father. Prepare to die. BTW my number is: 03-232323.
- Partial intersection - the number 03-2323 is recognized as a PHONE_NUMBER but 232323 is
  recognized as SSN:
  My name is Inigo Montoya. You Killed my Father. Prepare to die. BTW my number is: <
  PHONE_NUMBER><SSN>.

## Installation

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

### As service:

In folder presidio/presidio-anonymizer run:

```
pipenv sync
```

Start the server with flask (***this is a test server please do not use in prod***):

```
pipenv run app.py
```

The request should be:

```
POST /anonymize
```

[comment]: <shiranr> (TODO add result example when anonymizer is ready 2626)

```
RESULT
```

Payload:

```json
{
  "text": "hello world, my name is Jane Doe. My number is: 034453334",
  "transformations": {
    "DEFAULT": {
      "type": "replace"
    },
    "PHONE_NUMBER": {
      "type": "mask",
      "masking_char": "*",
      "chars_to_mask": 4,
      "from_end": true
    }
  },
  "analyzer_results": [
    {
      "start": 24,
      "end": 32,
      "score": 0.8,
      "entity_type": "NAME"
    },
    {
      "start": 24,
      "end": 28,
      "score": 0.8,
      "entity_type": "FIRST_NAME"
    },
    {
      "start": 29,
      "end": 32,
      "score": 0.6,
      "entity_type": "LAST_NAME"
    },
    {
      "start": 48,
      "end": 57,
      "score": 0.95,
      "entity_type": "PHONE_NUMBER"
    }
  ]
}
```

