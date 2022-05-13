# Example 11: Custom anonymization

Presidio-anonymizer can accept arbitrary operations to perform on identified entities.
These operations can be passed in the form of a lambda function.

In the following example, we use fake values to perform pseudonymization.
First, let's look at the operator:

<!--pytest-codeblocks:cont-->
```python
from faker import Faker
from presidio_anonymizer.entities import OperatorConfig

fake = Faker()

# Create faker function (note that it has to receive a value)
def fake_name(x):
    return fake.name()


# Create custom operator for the PERSON entity
operators = {"PERSON": OperatorConfig("custom", {"lambda": fake_name})}
```

Full example:

<!--pytest-codeblocks:cont-->
```python
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig, EngineResult, RecognizerResult
from faker import Faker


fake = Faker()

# Create faker function (note that it has to receive a value)
def fake_name(x):
    return fake.name()


# Create custom operator for the PERSON entity
operators = {"PERSON": OperatorConfig("custom", {"lambda": fake_name})}

# Analyzer output
analyzer_results = [RecognizerResult(entity_type="PERSON", start=11, end=18, score=0.8)]

text_to_anonymize = "My name is Raphael and I like to fish."

anonymizer = AnonymizerEngine()

anonymized_results = anonymizer.anonymize(
    text=text_to_anonymize, analyzer_results=analyzer_results, operators=operators
)

print(anonymized_results.text)
```

This is a simple example, but here are some examples for more advanced anonymization options:

- Identify the gender and create a random value from the same gender (e.g., Laura -> Pam)
- Identifying the date pattern and perform date shift (01-01-2020 -> 05-01-2020)
- Identify the age and bucket by decade (89 -> 80-90)
