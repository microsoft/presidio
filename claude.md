# Presidio - Claude Code Guide

## Overview

**Presidio** (Latin for "protection, garrison") is Microsoft's comprehensive Data Protection and De-identification SDK. It provides fast, context-aware, pluggable, and customizable PII (Personally Identifiable Information) detection and anonymization services for text, images, and structured data.

**Repository**: https://github.com/microsoft/presidio
**Documentation**: https://microsoft.github.io/presidio
**Demo**: https://aka.ms/presidio-demo

## Key Features

1. **Predefined & Custom PII Recognizers** - Leverages NER, regex, rule-based logic, and checksums with contextual awareness in multiple languages
2. **External Model Integration** - Connect to third-party PII detection models
3. **Multiple Deployment Options** - Python packages, PySpark, Docker, Kubernetes
4. **Highly Customizable** - Extensible PII identification and de-identification
5. **Image Redaction** - Redact PII from standard images and DICOM medical images

## Repository Structure

```
presidio/
├── presidio-analyzer/        # PII identification in text
├── presidio-anonymizer/      # De-identify detected PII entities
├── presidio-image-redactor/  # Redact PII from images using OCR
├── presidio-structured/      # PII identification in structured/semi-structured data
├── presidio-cli/             # Command-line interface
├── docs/                     # Comprehensive documentation
├── e2e-tests/               # End-to-end tests
├── .devcontainer/           # Development container configuration
└── docker-compose*.yml      # Docker deployment configurations
```

## Core Components

### 1. Presidio Analyzer

**Purpose**: Identify PII entities in text using NLP and pattern matching.

**Key Classes**:
- `AnalyzerEngine` - Main entry point for PII analysis
- `RecognizerResult` - Contains detected PII information
- `EntityRecognizer` - Base class for custom recognizers
- `PatternRecognizer` - Pattern-based recognition
- `AnalyzerEngineProvider` - Factory for creating analyzer instances

**Basic Usage**:
```python
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
results = analyzer.analyze(
    text="My phone number is 212-555-5555",
    entities=["PHONE_NUMBER"],
    language='en'
)
```

**Supported Entities**: CREDIT_CARD, CRYPTO, DATE_TIME, EMAIL_ADDRESS, IBAN_CODE, IP_ADDRESS, NRP, LOCATION, PERSON, PHONE_NUMBER, MEDICAL_LICENSE, URL, US_SSN, US_PASSPORT, UK_NHS, and many more (see docs/supported_entities.md for full list)

**Location**: `presidio-analyzer/presidio_analyzer/`

### 2. Presidio Anonymizer

**Purpose**: De-identify detected PII using various operators (redact, replace, encrypt, hash, mask, etc.).

**Key Classes**:
- `AnonymizerEngine` - Main entry point for anonymization
- `OperatorConfig` - Configuration for anonymization operators
- `DeanonymizeEngine` - Reverse anonymization when using reversible operators

**Basic Usage**:
```python
from presidio_anonymizer import AnonymizerEngine

anonymizer = AnonymizerEngine()
anonymized = anonymizer.anonymize(
    text="My phone number is 212-555-5555",
    analyzer_results=results
)
```

**Anonymization Operators**:
- `replace` - Replace with a new value
- `redact` - Remove the PII
- `hash` - Hash the PII
- `mask` - Mask characters
- `encrypt` - Encrypt the PII (reversible)
- `custom` - Custom anonymization logic

**Location**: `presidio-anonymizer/presidio_anonymizer/`

### 3. Presidio Image Redactor

**Purpose**: Detect and redact PII from images using OCR and the analyzer.

**Key Classes**:
- `ImageRedactorEngine` - Main entry point for image redaction
- `ImageAnalyzerEngine` - Analyze images for PII
- `DicomImageRedactorEngine` - Specialized for DICOM medical images

**Basic Usage**:
```python
from presidio_image_redactor import ImageRedactorEngine
from PIL import Image

engine = ImageRedactorEngine()
image = Image.open("image_with_pii.png")
redacted_image = engine.redact(image)
```

**Location**: `presidio-image-redactor/presidio_image_redactor/`

### 4. Presidio Structured

**Purpose**: Detect and anonymize PII in structured/semi-structured data (JSON, CSV, Parquet, DataFrames).

**Key Classes**:
- `StructuredEngine` - Main entry point for structured data
- `BatchAnalyzerEngine` - Batch analysis for structured data
- `DictAnalyzerResult` - Results for dictionary/JSON data

**Basic Usage**:
```python
from presidio_structured import StructuredEngine
import pandas as pd

engine = StructuredEngine()
df = pd.DataFrame({"name": ["John"], "phone": ["212-555-5555"]})
anonymized_df = engine.anonymize(df)
```

**Location**: `presidio-structured/presidio_structured/`

### 5. Presidio CLI

**Purpose**: Command-line interface for quick PII detection and anonymization.

**Location**: `presidio-cli/`

## Installation

### Using pip (Python 3.8 - 3.13):
```bash
# Analyzer with default spaCy model
pip install presidio-analyzer
python -m spacy download en_core_web_lg

# Anonymizer
pip install presidio-anonymizer

# Image Redactor
pip install presidio-image-redactor

# Structured
pip install presidio-structured

# CLI
pip install presidio-cli
```

### Using Docker:
```bash
# Pull images
docker pull mcr.microsoft.com/presidio-analyzer
docker pull mcr.microsoft.com/presidio-anonymizer
docker pull mcr.microsoft.com/presidio-image-redactor

# Run with docker-compose
docker-compose up
```

### From Source:
```bash
# Install all components in development mode
pip install -e ./presidio-analyzer
pip install -e ./presidio-anonymizer
pip install -e ./presidio-image-redactor
pip install -e ./presidio-structured
pip install -e ./presidio-cli
```

## Common Workflows

### Text Anonymization Workflow

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# 1. Initialize engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# 2. Analyze text for PII
text = "My name is John Doe and my email is john@example.com"
results = analyzer.analyze(text=text, language='en')

# 3. Anonymize detected PII
anonymized = anonymizer.anonymize(text=text, analyzer_results=results)

print(f"Original: {text}")
print(f"Anonymized: {anonymized.text}")
```

### Custom Recognizer Workflow

```python
from presidio_analyzer import PatternRecognizer, Pattern

# Create custom recognizer for employee IDs
employee_id_recognizer = PatternRecognizer(
    supported_entity="EMPLOYEE_ID",
    patterns=[Pattern("emp_id_pattern", r"EMP-\d{6}", 0.9)]
)

# Add to analyzer
analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(employee_id_recognizer)

# Use analyzer
results = analyzer.analyze("My ID is EMP-123456", language='en')
```

### Image Redaction Workflow

```python
from presidio_image_redactor import ImageRedactorEngine
from PIL import Image

# Load image
image = Image.open("document.png")

# Redact PII
engine = ImageRedactorEngine()
redacted_image = engine.redact(image)

# Save result
redacted_image.save("document_redacted.png")
```

## Development Setup

### Prerequisites
- Python 3.8 - 3.13
- Docker (optional, for containerized development)
- VS Code (optional, .devcontainer available)

### Setting Up Development Environment

```bash
# 1. Clone repository
git clone https://github.com/microsoft/presidio.git
cd presidio

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies for all modules
pip install -e ./presidio-analyzer[dev]
pip install -e ./presidio-anonymizer[dev]
pip install -e ./presidio-image-redactor[dev]
pip install -e ./presidio-structured[dev]

# 4. Install pre-commit hooks
pip install pre-commit
pre-commit install

# 5. Download NLP models
python -m spacy download en_core_web_lg
```

### Using Dev Container
```bash
# Open in VS Code with Remote-Containers extension
# The .devcontainer configuration will handle setup automatically
```

## Testing

### Running Tests

```bash
# Run tests for a specific module
cd presidio-analyzer
pytest

# Run with coverage
pytest --cov=presidio_analyzer --cov-report=html

# Run all tests from root
pytest presidio-analyzer/tests
pytest presidio-anonymizer/tests
pytest presidio-image-redactor/tests
pytest presidio-structured/tests

# Run end-to-end tests
cd e2e-tests
pytest
```

### Running Linter/Formatter
```bash
# Format code with ruff
ruff format .

# Lint code
ruff check .

# Run pre-commit checks
pre-commit run --all-files
```

## Docker Deployment

### Single Module
```bash
# Build analyzer
docker build -f presidio-analyzer/Dockerfile -t presidio-analyzer .

# Run analyzer
docker run -p 5002:3000 presidio-analyzer
```

### Full Stack
```bash
# Start all services
docker-compose up

# Analyzer API: http://localhost:5002
# Anonymizer API: http://localhost:5001
```

### Using the REST API

```bash
# Analyze text
curl -X POST http://localhost:5002/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "My SSN is 123-45-6789", "language": "en"}'

# Anonymize text
curl -X POST http://localhost:5001/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "My SSN is 123-45-6789",
    "analyzer_results": [
      {"start": 10, "end": 21, "score": 0.95, "entity_type": "US_SSN"}
    ]
  }'
```

## Key Configuration Options

### Analyzer Configuration

```python
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

# Custom NLP engine (e.g., transformers)
nlp_config = {
    "nlp_engine_name": "transformers",
    "models": [{"lang_code": "en", "model_name": "dslim/bert-base-NER"}]
}
nlp_engine = NlpEngineProvider(nlp_configuration=nlp_config).create_engine()

analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

# Analyze with specific entities only
results = analyzer.analyze(
    text="...",
    entities=["PHONE_NUMBER", "EMAIL_ADDRESS"],
    language='en',
    score_threshold=0.7  # Minimum confidence score
)
```

### Anonymizer Configuration

```python
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

anonymizer = AnonymizerEngine()

# Custom operators per entity type
operators = {
    "PHONE_NUMBER": OperatorConfig("mask", {"chars_to_mask": 4, "masking_char": "*"}),
    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
    "PERSON": OperatorConfig("hash", {"hash_type": "sha256"}),
}

result = anonymizer.anonymize(
    text=text,
    analyzer_results=results,
    operators=operators
)
```

## Multi-Language Support

Presidio supports multiple languages. Key languages include:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Dutch (nl)
- Hebrew (he)
- Russian (ru)
- Polish (pl)
- And more...

```python
# Using a different language
analyzer = AnalyzerEngine()
results = analyzer.analyze(
    text="Mon numéro de téléphone est 01 23 45 67 89",
    language='fr'
)
```

## Extending Presidio

### Creating Custom Recognizers

See `docs/analyzer/developing_recognizers.md` for detailed guide.

### Creating Custom Anonymizers

See `docs/anonymizer/adding_operators.md` for detailed guide.

### Integrating External Services

See `docs/tutorial/04_external_services.md` for integrating services like Azure AI Language.

## Important Files & Directories

| Path | Purpose |
|------|---------|
| `docs/` | Comprehensive documentation (MkDocs) |
| `docs/tutorial/` | Step-by-step tutorials |
| `docs/samples/` | Usage examples and deployment samples |
| `docs/api/` | Python API reference |
| `CONTRIBUTING.md` | Contribution guidelines |
| `SECURITY.md` | Security policy |
| `CHANGELOG.md` | Version history |
| `mkdocs.yml` | Documentation site configuration |
| `pyproject.toml` | Ruff linter/formatter configuration |
| `.pre-commit-config.yaml` | Pre-commit hooks configuration |

## Build & Release

See `docs/build_release.md` for information on:
- Building Python packages
- Building Docker images
- Release process
- Version management

## Common Issues & FAQ

See `docs/faq.md` for frequently asked questions including:
- Performance optimization
- Accuracy improvement
- Custom entity types
- Memory usage
- Integration patterns

## Support & Contributing

- **Issues**: https://github.com/microsoft/presidio/issues
- **Discussions**: https://github.com/microsoft/presidio/discussions
- **Email**: presidio@microsoft.com
- **Contributing Guide**: See CONTRIBUTING.md
- **Code of Conduct**: See CODE_OF_CONDUCT

## License

MIT License - See LICENSE file

## Warning

Presidio uses automated detection mechanisms. There is no guarantee that Presidio will find all sensitive information. Additional systems and protections should be employed in production environments.

## Quick Reference - Common Commands

```bash
# Install all components
pip install presidio-analyzer presidio-anonymizer presidio-image-redactor presidio-structured

# Run tests
pytest presidio-analyzer/tests

# Format code
ruff format .

# Build docs locally
mkdocs serve

# Run docker services
docker-compose up

# Run pre-commit checks
pre-commit run --all-files
```

## Next Steps

1. Read the [Getting Started Guide](docs/getting_started.md)
2. Explore [Tutorials](docs/tutorial/index.md)
3. Check [Sample Implementations](docs/samples/index.md)
4. Review [API Documentation](docs/api/analyzer_python.md)
5. See [Deployment Examples](docs/samples/deployments/index.md)
