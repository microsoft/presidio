# Getting started with structured and semi-structured de-identification with Presidio

Presidio-structured is a package built on top of Presidio that provides a simple way to de-identify structured and semi-structured data by detecting and anonymizing personally identifiable information (PII).

Presidio-structured supports the detection and anonymization of PII in tables (e.g. Pandas DataFrames or SQL tables) and semi-structured data (e.g. JSON).

!!! warning "Warning"
    **Alpha**: This package is currently in alpha, meaning it is in its early stages of development. Features and functionality may change as the project evolves.

## Simple flow - structured data

```python
import pandas as pd
from presidio_structured import StructuredEngine, PandasAnalysisBuilder
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker # optionally using faker as an example

# Initialize the engine with a Pandas data processor (default)
pandas_engine = StructuredEngine()

# Create a sample DataFrame
sample_df = pd.DataFrame({'name': ['John Doe', 'Jane Smith'], 'email': ['john.doe@example.com', 'jane.smith@example.com']})

# Generate a tabular analysis which detects the PII entities in the DataFrame.
tabular_analysis = PandasAnalysisBuilder().generate_analysis(sample_df)

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

## Read more

- [Presidio structured documentation](../structured/index.md)
- [Presidio structured sample notebook](../samples/python/example_structured.ipynb)
