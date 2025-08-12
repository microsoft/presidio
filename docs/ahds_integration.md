# Azure Health Data Services (AHDS) Integration

Presidio supports integration with Azure Health Data Services (AHDS) for both entity recognition and anonymization with realistic surrogate generation.

## Resources

- [Azure Health Data Services Documentation](https://learn.microsoft.com/en-us/azure/healthcare-apis/deidentification/)
- [Azure Health Deidentification Python SDK](https://pypi.org/project/azure-health-deidentification/)

## Overview

The AHDS integration provides two main capabilities:

1. **AHDS Recognizer** (in presidio-analyzer): Detects PHI entities using Azure Health Data Services
2. **AHDS Surrogate Operator** (in presidio-anonymizer): Generates realistic surrogates using the SurrogateOnly operation

## Benefits of AHDS Surrogation

- **Maintains Data Utility**: Preserves structure and format for downstream analytics
- **Realistic Healthcare Context**: Generates medically plausible names, dates, and identifiers
- **Consistent Cross-References**: Same entity gets same surrogate throughout document
- **Format Preservation**: Maintains original formatting and linguistic patterns
- **Regulatory Compliance**: Meets HIPAA Safe Harbor requirements while maximizing utility

## Installation

### For AHDS Recognizer
```bash
pip install presidio-analyzer[ahds]
```

### For AHDS Surrogate Operator
```bash
pip install presidio-anonymizer[ahds]
```

## Prerequisites

- Azure Health Data Services endpoint
- Azure authentication configured (DefaultAzureCredential)
- Environment variables:
  - `AHDS_ENDPOINT`: Your AHDS service endpoint

## Complete Workflow Example

```python
import os
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Set your AHDS endpoint
os.environ["AHDS_ENDPOINT"] = "https://your-ahds-endpoint.api.eus001.deid.azure.com"

# Initialize engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Medical text with PHI
text = "Patient John Doe was seen by Dr. Smith on 2024-01-15 for diabetes treatment."

# Step 1: Detect entities using AHDS recognizer
analyzer_results = analyzer.analyze(
    text=text,
    entities=["PATIENT", "DOCTOR", "DATE"],
    language="en"
)

# Step 2: Anonymize using AHDS surrogate generation
result = anonymizer.anonymize(
    text=text,
    analyzer_results=analyzer_results,
    operators={
        "DEFAULT": OperatorConfig("surrogate", {
            "entities": analyzer_results,
            "input_locale": "en-US",
            "surrogate_locale": "en-US"
        })
    },
)

print(f"Original: {text}")
print(f"Anonymized: {result.text}")
# Output: "Patient Michael Johnson was seen by Dr. Brown on 1987-06-23 for diabetes treatment."
```

**Note:** This example uses the Azure Health Data Services SurrogateOnly operation, which provides superior data utility by generating realistic, medically-appropriate surrogates while maintaining document structure and relationships.

## Configuration Options

### AHDS Surrogate Operator Parameters

- `endpoint`: AHDS endpoint (optional, uses `AHDS_ENDPOINT` env var)
- `entities`: List of entities detected by analyzer
- `input_locale`: Input locale (default: "en-US")
- `surrogate_locale`: Surrogate locale (default: "en-US")

## Authentication

The AHDS integration uses Azure's `DefaultAzureCredential`, which supports multiple authentication methods:

1. Environment variables (Service Principal)
2. Managed Identity (when running on Azure)
3. Azure CLI (`az login`)
4. Visual Studio/VS Code credentials
5. Interactive browser login

For production deployments, we recommend using Service Principal or Managed Identity.

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Install the AHDS optional dependencies
   ```bash
   pip install presidio-analyzer[ahds] presidio-anonymizer[ahds]
   ```

2. **Authentication errors**: Ensure Azure credentials are properly configured
   ```bash
   az login  # For local development
   ```

3. **Endpoint not found**: Verify the `AHDS_ENDPOINT` environment variable is set correctly

### Testing without AHDS

The AHDS operators gracefully handle missing dependencies and will be skipped if not available. Tests will be automatically skipped if the `AHDS_ENDPOINT` environment variable is not set.

## See Also

- [Presidio Analyzer](../analyzer/index.md)
- [Presidio Anonymizer](../anonymizer/index.md)
- [Azure Health Data Services Documentation](https://docs.microsoft.com/en-us/azure/healthcare-apis/)
