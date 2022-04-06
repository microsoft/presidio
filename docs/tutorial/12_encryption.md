# Example 12: Encryption and decryption

This sample shows how to use Presidio Anonymizer built-in functionality, to encrypt and decrypt identified entities. The encryption is using AES cypher in CBC mode and requires a cryptographic key as an input for both the encryption and the decryption.

## Set up imports

<!--pytest-codeblocks:cont-->
```python
from presidio_anonymizer import AnonymizerEngine, DeanonymizeEngine
from presidio_anonymizer.entities import (
    RecognizerResult,
    OperatorResult,
    OperatorConfig,
)
```

## Define a cryptographic key (for both encryption and decryption)

<!--pytest-codeblocks:cont-->
```python
crypto_key = "WmZq4t7w!z%C&F)J"
```

## Presidio Anonymizer: Encrypt
<!--pytest-codeblocks:skip-->
```python
engine = AnonymizerEngine()

# Invoke the anonymize function with the text,
# analyzer results (potentially coming from presidio-analyzer)
# and an 'encrypt' operator to get an encrypted anonymization output:
anonymize_result = engine.anonymize(
    text="My name is James Bond",
    analyzer_results=[
        RecognizerResult(entity_type="PERSON", start=11, end=21, score=0.8),
    ],
    operators={"PERSON": OperatorConfig("encrypt", {"key": crypto_key})},
)

anonymize_result
```

The output contains both the anonymized text, as well as the location of the encrypted entities. This is useful as we would need to decrypt only the entities and not the full text:

<!--pytest-codeblocks:skip-->
```python
# Fetch the anonymized text from the result.
anonymized_text = anonymize_result.text

# Fetch the anonynized entities from the result.
anonymized_entities = anonymize_result.items
```

## Presidio Anonymizer: Decrypt

<!--pytest-codeblocks:skip-->
```python
# Initialize the engine:
engine = DeanonymizeEngine()

# Invoke the deanonymize function with the text, anonymizer results
# and a 'decrypt' operator to get the original text as output.
deanonymized_result = engine.deanonymize(
    text=anonymized_text,
    entities=anonymized_entities,
    operators={"DEFAULT": OperatorConfig("decrypt", {"key": crypto_key})},
)

deanonymized_result
```

## Alternatively, call the Decrypt operator directly

<!--pytest-codeblocks:skip-->
```python
from presidio_anonymizer.operators import Decrypt

# Fetch the encrypted entity value from the previous stage
encrypted_entity_value = anonymize_result.items[0].text

# Restore the original entity value
Decrypt().operate(text=encrypted_entity_value, params={"key": crypto_key})
```
