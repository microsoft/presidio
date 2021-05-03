# Presidio anonymizer

## Description

The Presidio anonymizer is a Python based module for anonymizing detected PII text
entities with desired values.

![Anonymizer Design](../docs/assets/anonymizer-design.png)

### Deploy Presidio anonymizer to Azure

Use the following button to deploy presidio anonymizer to your Azure subscription.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Fpresidio%2Fmain%2Fpresidio-anonymizer%2Fdeploytoazure.json)


### Anonymizer

Presidio anonymizer comes by default with the following anonymizers:

-   Replace - replaces the PII with desired value

    Parameters: `new_value` - replaces existing text with the given value.

    If `new_value` is not supplied or empty, default behavior will be: <entity_type>
    e.g: <PHONE_NUMBER>

-   Redact - removes the PII completely from text Parameters: None
-   Hash - hash the PII using either sha256, sha512 or md5. Parameters:
    -   `hash_type` - sets the type of hashing. can be either sha256, sha512 or md5.
        The default hash type is sha256.
-   Mask - replaces the PII with a given character.

    Parameters:

    -   `chars_to_mask` - the amount of characters out of the PII that should be
        replaced.
    -   `masking_char` - the character to be replaced with.
    -   `from_end` - Whether to mask the PII from it's end.
    
-   Encrypt - replaced the PII with an encrypted text. 
-   Custom - replace the PII with the result of the function executed on the PII

    Parameters: `lambda` - lambda to execute on the PII data

    The lambda return type must be a string


Anonymizer currently uses Advanced Encryption Standard (AES) as the encryption algorithm, also known as Rijndael. 

    Parameters:

    -   `key` - a cryptographic key used for the encryption.
    The length of the key needs to be of 128, 192 or 256 bits, in a string format.

Please notice: if default value is not stated in anonymizers object, the default
anonymizer is "replace" for all entities. The replacing value will be the entity type
e.g.: <PHONE_NUMBER>

As the input text could potentially have overlapping PII entities, there are different
anonymization scenarios:

-   No overlap (single PII) - single PII over text entity, uses a given or default
    anonymizer to anonymize and replace the PII text entity.
-   Full overlap of PIIs - When one text have several PIIs, the PII with the higher score
    will be taken. Between PIIs with identical scores, the selection will be arbitrary.
-   One PII is contained in another - anonymizer will use the PII with larger text.
-   Partial intersection - both will be returned concatenated.

Example of how each scenario would work. Our text will be:

My name is Inigo Montoya. You Killed my Father. Prepare to die. BTW my number is:
03-232323.

-   No overlaps - only Inigo was recognized as NAME:
    My name is <NAME> Montoya. You Killed my Father. Prepare to die. BTW my number is:
    03-232323.
-   Full overlap - the number was recognized as PHONE_NUMBER with score of 0.7 and as SSN
    with score of 0.6, we will take the higher score:
    My name is Inigo Montoya. You Killed my Father. Prepare to die. BTW my number is: <
    PHONE_NUMBER>
-   One PII is contained is another - Inigo was recognized as FIRST_NAME and Inigo Montoya
    was recognized as NAME, we will take the larger one:
    My name is <NAME>. You Killed my Father. Prepare to die. BTW my number is: 03-232323.
-   Partial intersection - the number 03-2323 is recognized as a PHONE_NUMBER but 232323
    is recognized as SSN:
    My name is Inigo Montoya. You Killed my Father. Prepare to die. BTW my number is: <
    PHONE_NUMBER><SSN>.

### Deanonymizer

Presidio deanonymize currently contains one operator:

-   Decrypt - replaced the encrypted text with decrypted text. Uses Advanced Encryption Standard (AES) as the encryption algorithm, also known as Rijndael. 

    Parameters:

    -   `key` - a cryptographic key used for the encryption.
    The length of the key needs to be of 128, 192 or 256 bits, in a string format.

Please notice: you can use "DEFAULT" as an operator key to define an operator over all entities.

## Installation

### As package:

To get started with Presidio-anonymizer, run the following:

```sh
pip install presidio-anonymizer
```

#### Getting started

```python
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities.engine import RecognizerResult, OperatorConfig

# Initialize the engine with logger.
engine = AnonymizerEngine()

# Invoke the anonymize function with the text, analyzer results and
# Operators to define the anonymization type.
result = engine.anonymize(
    text="My name is Bond, James Bond",
    analyzer_results=[RecognizerResult("PERSON", 11, 15, 0.8),
                      RecognizerResult("PERSON", 17, 27, 0.8)],
    operators={"PERSON": OperatorConfig("replace", {"new_value": "BIP"})}
)

print(result)

```
This example take the output of the AnonymizerEngine with encrypted PII entities, 
and decrypt it back to the original text:
```python
from presidio_anonymizer import DeanonymizeEngine
from presidio_anonymizer.entities.engine import AnonymizerResult, OperatorConfig

# Initialize the engine with logger.
engine = DeanonymizeEngine()

# Invoke the deanonymize function with the text, anonymizer results and
# Operators to define the deanonymization type.
result = engine.deanonymize(
    text="My name is S184CMt9Drj7QaKQ21JTrpYzghnboTF9pn/neN8JME0=",
    entities=[AnonymizerResult(start=11, end=55, entity_type="PERSON"),],
    operators={"DEFAULT": OperatorConfig("decrypt", {"key": "WmZq4t7w!z%C&F)J"})}
)

print(result)

```

### As docker service:

In folder presidio/presidio-anonymizer run:

```
docker-compose up -d
```

### HTTP API

Follow the [API Spec](https://microsoft.github.io/presidio/api-docs/api-docs.html#tag/Anonymizer) for the
Anonymizer REST API reference details
