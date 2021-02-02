# Presidio anonymizer

## Description

The Presidio anonymizer is a Python based module for anonymizing detected PII text
entities with desired values.

[comment]: <shiranr> (#TODO need to fill this once the the functionality is done 2656 - 2659)
Presidio anonymizer comes by default with the following anonymizers:

- Replace - replaces the PII with desired value <br>
  Parameters: "new_value" - replaces existing text with the given value. <br>
  If "new_value" is not supplied or empty, default behavior will be: <entity_type>
  e.g: <PHONE_NUMBER>
- Redact - removes the PII completely from text Parameters: None
- Hash - hash the PII using sha256
- FPE - using ff1 algorithm for formatting-Preserving Encryption on the PII
- Mask - replaces the PII with a given character. <br>
  Parameters: 
  * "chars_to_mask" - the amount of characters out of the PII that should
   be replaced. 
  * "masking_char" - the character to be replaced with. 
  * "from_end" - Whether to mask the PII from it's end.


Please notice: if default value is not stated in transformations object, the default
anonymizer is "replace" for all entities. The replacing value will be the entity type
e.g.: <PHONE_NUMBER>

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

AnonymizerRequest receives a json (e.g. test/payload.json), validate the json format and
returns an object the engine can use and anonymize.

```python
import os
from presidio_anonymizer.anonymizer_engine import AnonymizerEngine
from presidio_anonymizer.entities import AnonymizerRequest

json_path = os.path.dirname(__file__) + "/test/resources/payload.json"
with open(json_path) as json_file:
  data = AnonymizerRequest(json_file)
  text = AnonymizerEngine().anonymize(data)
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

Payload:
```json
{
  "text": "hello world, my name is Jane Doe. My number is: 034453334",
  "transformations": {
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
Result:
```
200 OK
hello world, my name is <NAME>. My number is: 03445****
```


### HTTP API

#### /anonymizers
Returns a list of supported anonymizers.

Method: GET

No paramaters are required.

Response sample:
```json
["mask", "fpe", "replace", "hash", "redact"]
```

### Deploy Presidio Anonymizer to Azure

TODO: change this link to main branch once merged (#2765).
[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Fpresidio%2FV2%2Fpresidio-anonymizer%2Fdeploytoazure.json)
