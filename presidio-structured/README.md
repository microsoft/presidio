# Presidio structured

## Status

**Alpha**: This package is currently in alpha, meaning it is in its early stages of development. Features and functionality may change as the project evolves.

## Description

The Presidio structured package is a flexible and customizable framework designed to identify and protect structured sensitive data. This tool extends the capabilities of Presidio, focusing on structured data formats such as tabular formats and semi-structured formats (JSON).

## Installation

### As a python package:

To install the `presidio-structured` package, run the following command:

```sh
pip install presidio-structured
```

#### Getting started

Example 1: Anonymizing DataFrames

```python
import pandas as pd
from presidio_structured import StructuredEngine, TabularAnalysisBuilder
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker # optionally using faker as an example

# Initialize the engine with a Pandas data processor (default)
pandas_engine = StructuredEngine()

# Create a sample DataFrame
sample_df = pd.DataFrame({'name': ['John Doe', 'Jane Smith'], 'email': ['john.doe@example.com', 'jane.smith@example.com']})

# Generate a tabular analysis which describes PII entities in the DataFrame.
tabular_analysis = TabularAnalysisBuilder().generate_analysis(sample_df)

# Define anonymization operators
fake = Faker()
operators = {
    "PERSON": OperatorConfig("replace", {"new_value": "REDACTED"}),
    "EMAIL_ADDRESS": OperatorConfig("custom", {"lambda": lambda x: fake.safe_email()})
}

# Anonymize DataFrame
anonymized_df = pandas_engine.anonymize(sample_df, tabular_analysis, operators=operators)
print(anonymized_df)
```

Example 2: Anonymizing JSON Data

```python
from presidio_structured import StructuredEngine, JsonAnalysisBuilder, StructuredAnalysis, JsonDataProcessor
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker # optionally using faker as an example

# Initialize the engine with a JSON data processor
json_engine = StructuredEngine(data_processor=JsonDataProcessor())


# Sample JSON data
sample_json = {
    "user": {
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
}

# Generate analysis for simple JSON data
json_analysis = JsonAnalysisBuilder().generate_analysis(sample_json)

# Define anonymization operators
fake = Faker() # using faker for email generation.
operators = {
    "PERSON": OperatorConfig("replace", {"new_value": "REDACTED"}),
    "EMAIL_ADDRESS": OperatorConfig("custom", {"lambda": lambda x: fake.safe_email()})
}

# Anonymize JSON data
anonymized_json = json_engine.anonymize(sample_json, json_analysis, operators=operators)
print(anonymized_json)

# Handling Json Data with nested objects in lists
sample_complex_json = {
    "users": [
        {"name": "John Doe", "email": "john.doe@example.com"},
        {"name": "Jane Smith", "email": "jane.smith@example.com"}
    ]
}

# Nesting objects in lists is not supported in JsonAnalysisBuilder for now,
# Manually defining the analysis for complex JSON data
json_complex_analysis = StructuredAnalysis(entity_mapping={
    "users.name": "PERSON",
    "users.email": "EMAIL_ADDRESS"
})

# Anonymize complex JSON data
anonymized_complex_json = json_engine.anonymize(sample_complex_json, json_complex_analysis, operators=operators)
print(anonymized_complex_json)
```
