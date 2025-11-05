---
name: presidio-pii-detection
description: A comprehensive skill for detecting, analyzing, and anonymizing Personally Identifiable Information (PII) in text, images, and structured data using Microsoft Presidio. Use this skill when you need to identify sensitive data like credit cards, SSNs, emails, phone numbers, names, locations, or create custom PII recognizers. Also use for redacting PII from documents, images, or data frames.
---

# Presidio PII Detection and Anonymization Skill

## Overview

You are now equipped with comprehensive knowledge of Microsoft Presidio, a powerful Data Protection and De-identification SDK. This skill enables you to help users detect and anonymize PII in various data formats.

## Core Capabilities

### 1. Text PII Detection and Anonymization

When a user needs to detect or anonymize PII in text:

1. **Use AnalyzerEngine** to identify PII entities:
```python
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
results = analyzer.analyze(
    text="User provided text",
    entities=["PHONE_NUMBER", "EMAIL_ADDRESS", "PERSON"],  # Specify or use None for all
    language='en',
    score_threshold=0.5  # Adjust confidence threshold
)
```

2. **Use AnonymizerEngine** to de-identify detected PII:
```python
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

anonymizer = AnonymizerEngine()

# With custom operators per entity type
operators = {
    "PHONE_NUMBER": OperatorConfig("mask", {"chars_to_mask": 4, "masking_char": "*"}),
    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
    "PERSON": OperatorConfig("hash", {"hash_type": "sha256"}),
    "CREDIT_CARD": OperatorConfig("encrypt", {"key": "WmZq4t7w!z%C&F)J"}),
}

anonymized_result = anonymizer.anonymize(
    text="User provided text",
    analyzer_results=results,
    operators=operators
)

print(anonymized_result.text)
```

### 2. Supported PII Entity Types

**Global Entities:**
- CREDIT_CARD - Credit card numbers with checksum validation
- CRYPTO - Cryptocurrency wallet addresses (Bitcoin)
- DATE_TIME - Dates, times, and time periods
- EMAIL_ADDRESS - Email addresses with RFC-822 validation
- IBAN_CODE - International Bank Account Numbers
- IP_ADDRESS - IPv4 and IPv6 addresses
- NRP - Nationality, religious, or political group
- LOCATION - Geographic locations (cities, countries, regions)
- PERSON - Full person names
- PHONE_NUMBER - Telephone numbers
- MEDICAL_LICENSE - Medical license numbers
- URL - Web URLs

**US Entities:**
- US_BANK_NUMBER - Bank account numbers
- US_DRIVER_LICENSE - Driver's licenses
- US_ITIN - Individual Taxpayer ID Numbers
- US_PASSPORT - Passport numbers
- US_SSN - Social Security Numbers

**Other Country-Specific:**
- UK_NHS, UK_NINO (UK)
- ES_NIF, ES_NIE (Spain)
- IT_FISCAL_CODE, IT_DRIVER_LICENSE, IT_VAT_CODE, IT_PASSPORT, IT_IDENTITY_CARD (Italy)
- PL_PESEL (Poland)
- SG_NRIC_FIN, SG_UEN (Singapore)
- AU_ABN, AU_ACN, AU_TFN, AU_MEDICARE (Australia)
- IN_PAN, IN_AADHAAR, IN_VEHICLE_REGISTRATION, IN_VOTER, IN_PASSPORT, IN_GSTIN (India)
- FI_PERSONAL_IDENTITY_CODE (Finland)
- KR_RRN (Korea)
- TH_TNIN (Thailand)

### 3. Custom PII Recognizer Creation

When users need to detect custom PII patterns:

```python
from presidio_analyzer import PatternRecognizer, Pattern, AnalyzerEngine

# Example: Detect custom employee IDs
employee_recognizer = PatternRecognizer(
    supported_entity="EMPLOYEE_ID",
    name="employee_id_recognizer",
    patterns=[
        Pattern(
            name="employee_id_pattern",
            regex=r"EMP-\d{6}",
            score=0.9
        )
    ],
    context=["employee", "emp", "staff", "worker"]  # Context words increase confidence
)

# Add to analyzer
analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(employee_recognizer)

# Use as normal
results = analyzer.analyze("My ID is EMP-123456", language='en')
```

### 4. Image PII Redaction

When users need to redact PII from images:

```python
from presidio_image_redactor import ImageRedactorEngine
from PIL import Image

# Load image
image = Image.open("path/to/image.png")

# Redact PII
engine = ImageRedactorEngine()
redacted_image = engine.redact(
    image,
    fill="background",  # or "solid" for black boxes
    padding_width=0.05  # Add padding around redacted areas
)

# Save result
redacted_image.save("path/to/redacted_image.png")
```

For DICOM medical images:
```python
from presidio_image_redactor import DicomImageRedactorEngine

engine = DicomImageRedactorEngine()
engine.redact_from_file(
    input_dicom_path="input.dcm",
    output_dicom_path="output.dcm",
    fill="background"
)
```

### 5. Structured Data PII Detection

When users need to anonymize DataFrames, CSV, JSON, or Parquet:

```python
from presidio_structured import StructuredEngine, PandasAnalysisBuilder
import pandas as pd

# Create sample DataFrame
df = pd.DataFrame({
    "name": ["John Doe", "Jane Smith"],
    "email": ["john@example.com", "jane@example.com"],
    "phone": ["212-555-5555", "415-555-1234"]
})

# Analyze and anonymize
engine = StructuredEngine()
anonymized_df = engine.anonymize(
    data=df,
    operators={
        "name": "mask",
        "email": "replace",
        "phone": "hash"
    }
)
```

### 6. Anonymization Operators

Available operators for different use cases:

- **replace** - Replace with a static value or entity type placeholder
  ```python
  OperatorConfig("replace", {"new_value": "<REDACTED>"})
  ```

- **redact** - Remove the PII entirely
  ```python
  OperatorConfig("redact", {})
  ```

- **hash** - Hash the PII (one-way, irreversible)
  ```python
  OperatorConfig("hash", {"hash_type": "sha256"})  # or "sha512", "md5"
  ```

- **mask** - Mask characters with a masking character
  ```python
  OperatorConfig("mask", {"chars_to_mask": 4, "masking_char": "*", "from_end": True})
  ```

- **encrypt** - Encrypt the PII (reversible with key)
  ```python
  OperatorConfig("encrypt", {"key": "your-encryption-key-16-bytes"})
  ```

- **keep** - Keep the original value (useful for allowlisting)
  ```python
  OperatorConfig("keep", {})
  ```

- **custom** - Use custom anonymization logic
  ```python
  OperatorConfig("custom", {"lambda": lambda x: f"ANON_{len(x)}"})
  ```

### 7. Multi-Language Support

When working with non-English text:

```python
analyzer = AnalyzerEngine()

# French
results = analyzer.analyze(
    text="Mon numéro est 01 23 45 67 89",
    language='fr'
)

# Spanish
results = analyzer.analyze(
    text="Mi correo es usuario@ejemplo.com",
    language='es'
)

# German
results = analyzer.analyze(
    text="Meine Telefonnummer ist 030-12345678",
    language='de'
)
```

Supported languages: en, es, fr, de, it, pt, nl, he, ru, pl, and more.

### 8. Using Transformers NLP Engine

For improved accuracy with transformer models:

```python
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import TransformersNlpEngine

# Configure transformers model
model_config = [{
    "lang_code": "en",
    "model_name": {
        "spacy": "en_core_web_sm",
        "transformers": "dslim/bert-base-NER"
    }
}]

nlp_engine = TransformersNlpEngine(models=model_config)
analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

results = analyzer.analyze(text="...", language='en')
```

### 9. Context-Aware Detection

Improve detection accuracy by providing context:

```python
from presidio_analyzer import PatternRecognizer, Pattern

# Custom recognizer with context awareness
account_recognizer = PatternRecognizer(
    supported_entity="ACCOUNT_NUMBER",
    patterns=[Pattern("account_pattern", r"\d{8,12}", 0.4)],  # Low initial score
    context=["account", "account number", "acct", "acc#"],  # Boost score when these appear nearby
    context_similarity_factor=0.35  # How much to boost
)
```

### 10. De-anonymization (Reversible Operations)

When encryption is used, de-anonymize later:

```python
from presidio_anonymizer import DeanonymizeEngine
from presidio_anonymizer.entities import OperatorConfig

# Anonymize with encryption
anonymizer = AnonymizerEngine()
encrypted_result = anonymizer.anonymize(
    text="My SSN is 123-45-6789",
    analyzer_results=results,
    operators={"US_SSN": OperatorConfig("encrypt", {"key": "encryption-key-16b"})}
)

# Later, de-anonymize
deanonymizer = DeanonymizeEngine()
original_result = deanonymizer.deanonymize(
    text=encrypted_result.text,
    entities=encrypted_result.items,
    operators={"US_SSN": OperatorConfig("decrypt", {"key": "encryption-key-16b"})}
)
```

## Decision Making Guidelines

### When to Use Which Component

1. **Use presidio-analyzer** when:
   - User needs to identify what PII exists in text
   - User wants to scan documents for sensitive data
   - User needs confidence scores for detected entities

2. **Use presidio-anonymizer** when:
   - User needs to de-identify detected PII
   - User wants to redact, mask, or replace sensitive data
   - User needs reversible anonymization (encryption)

3. **Use presidio-image-redactor** when:
   - User has images or PDFs with visible PII
   - User needs to redact text from scanned documents
   - User works with medical DICOM images

4. **Use presidio-structured** when:
   - User has CSV, JSON, Parquet, or DataFrame data
   - User needs to anonymize entire datasets
   - User wants to preserve data structure while removing PII

5. **Create custom recognizers** when:
   - User has organization-specific ID formats
   - Standard recognizers miss domain-specific patterns
   - User needs to detect non-standard PII types

## Common Patterns and Solutions

### Pattern 1: Full Text Anonymization Pipeline
```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

def anonymize_text(text, entities=None, language='en'):
    """Complete anonymization pipeline."""
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    # Detect PII
    results = analyzer.analyze(text=text, entities=entities, language=language)

    # Anonymize
    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)

    return anonymized.text, results
```

### Pattern 2: Batch Processing Multiple Documents
```python
from presidio_analyzer import AnalyzerEngine, BatchAnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

def batch_anonymize(documents):
    """Process multiple documents efficiently."""
    analyzer = AnalyzerEngine()
    batch_analyzer = BatchAnalyzerEngine(analyzer_engine=analyzer)
    anonymizer = AnonymizerEngine()

    # Analyze all documents
    batch_results = batch_analyzer.analyze_dict(documents, language='en')

    # Anonymize each
    anonymized_docs = []
    for doc_id, results in batch_results.items():
        anonymized = anonymizer.anonymize(
            text=documents[doc_id],
            analyzer_results=results
        )
        anonymized_docs.append(anonymized.text)

    return anonymized_docs
```

### Pattern 3: Allowlist Specific Values
```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

def anonymize_with_allowlist(text, allowed_emails):
    """Don't anonymize specific allowed values."""
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    results = analyzer.analyze(text=text, language='en')

    # Filter out allowed values
    filtered_results = [
        r for r in results
        if not (r.entity_type == "EMAIL_ADDRESS" and text[r.start:r.end] in allowed_emails)
    ]

    anonymized = anonymizer.anonymize(text=text, analyzer_results=filtered_results)
    return anonymized.text
```

### Pattern 4: Different Anonymization Per Entity Type
```python
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

def smart_anonymize(text, results):
    """Apply different strategies based on entity type."""
    anonymizer = AnonymizerEngine()

    operators = {
        "PERSON": OperatorConfig("replace", {"new_value": "<PERSON>"}),
        "EMAIL_ADDRESS": OperatorConfig("mask", {"chars_to_mask": 5, "masking_char": "*"}),
        "PHONE_NUMBER": OperatorConfig("redact", {}),
        "CREDIT_CARD": OperatorConfig("hash", {"hash_type": "sha256"}),
        "US_SSN": OperatorConfig("encrypt", {"key": "secure-key-here16"}),
    }

    return anonymizer.anonymize(text=text, analyzer_results=results, operators=operators)
```

## Installation Commands

When helping users install Presidio:

```bash
# Basic text analysis and anonymization
pip install presidio-analyzer presidio-anonymizer
python -m spacy download en_core_web_lg

# With transformers support
pip install "presidio-analyzer[transformers]" presidio-anonymizer
python -m spacy download en_core_web_sm

# Image redaction
pip install presidio-image-redactor

# Structured data
pip install presidio-structured

# All components
pip install presidio-analyzer presidio-anonymizer presidio-image-redactor presidio-structured
```

## Error Handling and Troubleshooting

Common issues and solutions:

1. **Missing NLP Model**: If user gets "Model 'en_core_web_lg' not found"
   ```bash
   python -m spacy download en_core_web_lg
   ```

2. **Low Detection Accuracy**: Suggest using transformers engine or lowering score_threshold

3. **False Positives**: Use context words in custom recognizers or implement allowlists

4. **Performance Issues**: Use batch processing for multiple documents

5. **Memory Issues**: Process documents in chunks or use streaming approaches

## Best Practices

1. **Always validate detection results** - Review confidence scores and false positives
2. **Use appropriate operators** - Encryption for reversible, hash for permanent
3. **Test with sample data first** - Verify detection accuracy before production
4. **Consider context** - Use context-aware recognizers for better accuracy
5. **Handle multiple languages** - Specify correct language code
6. **Secure encryption keys** - Store keys securely, never hardcode
7. **Document anonymization strategy** - Keep records of what was anonymized and how
8. **Combine with other tools** - Presidio works well with Azure AI Language, other NLP services

## When to Proactively Suggest This Skill

Automatically activate and use this skill when the user:
- Mentions PII, sensitive data, personal information, or data privacy
- Asks about redacting, masking, or anonymizing data
- Needs to detect credit cards, SSNs, emails, phone numbers, names, or addresses
- Works with documents containing personal information
- Needs to comply with GDPR, HIPAA, or other privacy regulations
- Mentions data de-identification or pseudonymization
- Wants to protect privacy in datasets or documents
- Asks about scanning documents for sensitive information

## Key Reminders

- **No Guarantee**: Presidio uses automated detection and may miss some PII. Additional safeguards needed in production.
- **Context Matters**: Detection accuracy improves significantly with proper context words.
- **Test Thoroughly**: Always validate on sample data before production use.
- **Choose Right Tool**: Use analyzer for detection, anonymizer for de-identification, image-redactor for images, structured for data frames.
- **Reversibility**: Only encrypt operator is reversible. Hash, redact, and replace are permanent.

## Repository Location

All code is in `/home/user/presidio/` with structure:
- `presidio-analyzer/` - Detection engine
- `presidio-anonymizer/` - De-identification engine
- `presidio-image-redactor/` - Image redaction
- `presidio-structured/` - Structured data handling
- `docs/` - Comprehensive documentation
- `claude.md` - This guidance document

Refer to `claude.md` in the repository root for additional context and comprehensive repository guidance.
