# Example 10: Simple anonymization

Once we have the identified PII entities, we can perform different de-identification operations on them. For more information on the supported operators, see [the anonymizer documentation](../anonymizer/index.md).

The anonymizer requires a configuration specifying the requested operation on each entity type. There's also a default operator which replaces a PII entity with the entity type name.

Each operator has a unique configuration with the parameters needed to perform the operation (redact, hash, mask, replace, encrypt etc.)

Here's an simple example of using presidio-anonymizer:

<!--pytest-codeblocks:cont-->
```python
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult

# Analyzer output
analyzer_results = [
    RecognizerResult(entity_type="PERSON", start=11, end=15, score=0.8),
    RecognizerResult(entity_type="PERSON", start=17, end=27, score=0.8),
]

# Initialize the engine:
engine = AnonymizerEngine()

# Invoke the anonymize function with the text,
# analyzer results (potentially coming from presidio-analyzer) and
# Operators to get the anonymization output:
result = engine.anonymize(
    text="My name is Bond, James Bond", analyzer_results=analyzer_results
)

print("De-identified text")
print(result.text)
```

To introduce additional operators, we can pass an `OperatorConfig`.
In this example we:

1. Mask the last 12 chars of a `PHONE_NUMBER` entity and replace them with `*`
2. Redact a `TITLE` entity
3. Replace all other entities with the string `<ANONYMIZED>`.

Defining the operators:

<!--pytest-codeblocks:cont-->
```python
# Define anonymization operators
operators = {
    "DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED>"}),
    "PHONE_NUMBER": OperatorConfig(
        "mask",
        {
            "type": "mask",
            "masking_char": "*",
            "chars_to_mask": 12,
            "from_end": True,
        },
    ),
    "TITLE": OperatorConfig("redact", {}),
}
```

Full example:

<!--pytest-codeblocks:cont-->
```python
from pprint import pprint
import json

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig, RecognizerResult


# Analyzer output
analyzer_results = [
    RecognizerResult(entity_type="PERSON", start=11, end=15, score=0.8),
    RecognizerResult(entity_type="PERSON", start=17, end=27, score=0.8),
]

text_to_anonymize = "My name is Bond, James Bond"

anonymizer = AnonymizerEngine()

# Define anonymization operators
operators = {
    "DEFAULT": OperatorConfig("replace", {"new_value": "<ANONYMIZED>"}),
    "PHONE_NUMBER": OperatorConfig(
        "mask",
        {
            "type": "mask",
            "masking_char": "*",
            "chars_to_mask": 12,
            "from_end": True,
        },
    ),
    "TITLE": OperatorConfig("redact", {}),
}

anonymized_results = anonymizer.anonymize(
    text=text_to_anonymize, analyzer_results=analyzer_results, operators=operators
)

print(f"text: {anonymized_results.text}")
print("detailed result:")

pprint(json.loads(anonymized_results.to_json()))
```
