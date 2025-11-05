# Presidio API Quick Reference

## AnalyzerEngine

### Basic Analysis
```python
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
results = analyzer.analyze(
    text: str,                    # Text to analyze
    entities: List[str] = None,   # Specific entities or None for all
    language: str = 'en',         # Language code
    score_threshold: float = 0.0, # Minimum confidence (0.0-1.0)
    return_decision_process: bool = False,
    ad_hoc_recognizers: List[EntityRecognizer] = None,
    context: List[str] = None,
    allow_list: List[str] = None
)
```

### RecognizerResult Properties
```python
result.entity_type      # e.g., "PHONE_NUMBER"
result.start           # Start position in text
result.end             # End position in text
result.score           # Confidence score (0.0-1.0)
result.analysis_explanation  # Detection reasoning
result.recognition_metadata  # Additional metadata
```

## AnonymizerEngine

### Basic Anonymization
```python
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

anonymizer = AnonymizerEngine()
result = anonymizer.anonymize(
    text: str,
    analyzer_results: List[RecognizerResult],
    operators: Dict[str, OperatorConfig] = None,  # Per-entity operators
    conflict_resolution: str = "merge_similar_or_contained"
)

# Result properties
result.text      # Anonymized text
result.items     # List of anonymized entities with metadata
```

### Operator Configuration
```python
# Replace
OperatorConfig("replace", {"new_value": "<REDACTED>"})

# Redact
OperatorConfig("redact", {})

# Hash
OperatorConfig("hash", {"hash_type": "sha256"})  # or "sha512", "md5"

# Mask
OperatorConfig("mask", {
    "chars_to_mask": int,      # Number of characters to mask
    "masking_char": str,       # Character to use (default "*")
    "from_end": bool          # Mask from end (default True)
})

# Encrypt (reversible)
OperatorConfig("encrypt", {"key": "16-byte-key-here"})

# Keep (no anonymization)
OperatorConfig("keep", {})
```

## Custom Pattern Recognizer

```python
from presidio_analyzer import PatternRecognizer, Pattern

recognizer = PatternRecognizer(
    supported_entity: str,            # e.g., "EMPLOYEE_ID"
    name: str = None,                # Recognizer name
    patterns: List[Pattern],          # List of patterns to match
    context: List[str] = None,       # Context words to boost score
    supported_language: str = "en",
    context_similarity_factor: float = 0.35
)

pattern = Pattern(
    name: str,           # Pattern identifier
    regex: str,          # Regular expression
    score: float         # Confidence score (0.0-1.0)
)
```

## ImageRedactorEngine

```python
from presidio_image_redactor import ImageRedactorEngine
from PIL import Image

engine = ImageRedactorEngine()
redacted_image = engine.redact(
    image: Image,
    fill: str = "background",     # "background" or "solid"
    padding_width: float = 0.05,  # Padding around redactions
    entities: List[str] = None,   # Specific entities or None
    **text_analyzer_kwargs        # Pass to analyzer
)
```

## DICOM Image Redaction

```python
from presidio_image_redactor import DicomImageRedactorEngine

engine = DicomImageRedactorEngine()
engine.redact_from_file(
    input_dicom_path: str,
    output_dicom_path: str,
    fill: str = "background",
    padding_width: int = 25,
    crop_ratio: float = 0.75,
    use_metadata: bool = True
)
```

## StructuredEngine (DataFrames)

```python
from presidio_structured import StructuredEngine
import pandas as pd

engine = StructuredEngine()

# Anonymize DataFrame
anonymized_df = engine.anonymize(
    data: pd.DataFrame,
    operators: Dict[str, Union[str, OperatorConfig]],
    entities: List[str] = None,
    language: str = 'en'
)
```

## BatchAnalyzerEngine

```python
from presidio_analyzer import AnalyzerEngine, BatchAnalyzerEngine

analyzer = AnalyzerEngine()
batch_analyzer = BatchAnalyzerEngine(analyzer_engine=analyzer)

# Analyze dictionary of documents
results = batch_analyzer.analyze_dict(
    input_dict: Dict[str, Any],
    language: str = 'en',
    **kwargs
)

# Analyze list of documents
results = batch_analyzer.analyze_iterator(
    texts: Iterator[Union[str, Dict]],
    language: str = 'en',
    **kwargs
)
```

## TransformersNlpEngine

```python
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import TransformersNlpEngine

model_config = [{
    "lang_code": "en",
    "model_name": {
        "spacy": "en_core_web_sm",           # For lemmas, tokens
        "transformers": "dslim/bert-base-NER"  # For NER
    }
}]

nlp_engine = TransformersNlpEngine(models=model_config)
analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
```

## DeanonymizeEngine (Reversible Operations)

```python
from presidio_anonymizer import DeanonymizeEngine
from presidio_anonymizer.entities import OperatorConfig

deanonymizer = DeanonymizeEngine()
original_result = deanonymizer.deanonymize(
    text: str,
    entities: List[OperatorResult],  # From anonymizer result.items
    operators: Dict[str, OperatorConfig]
)
```

## Entity Registry Management

```python
# Add custom recognizer
analyzer.registry.add_recognizer(custom_recognizer)

# Remove recognizer
analyzer.registry.remove_recognizer(recognizer_name)

# Load all recognizers
recognizers = analyzer.registry.load_predefined_recognizers()

# Get supported entities
entities = analyzer.registry.get_supported_entities()
```

## Common Entity Types

**Global**: CREDIT_CARD, CRYPTO, DATE_TIME, EMAIL_ADDRESS, IBAN_CODE, IP_ADDRESS, NRP, LOCATION, PERSON, PHONE_NUMBER, MEDICAL_LICENSE, URL

**US**: US_BANK_NUMBER, US_DRIVER_LICENSE, US_ITIN, US_PASSPORT, US_SSN

**UK**: UK_NHS, UK_NINO

**Spain**: ES_NIF, ES_NIE

**Italy**: IT_FISCAL_CODE, IT_DRIVER_LICENSE, IT_VAT_CODE, IT_PASSPORT, IT_IDENTITY_CARD

**Other**: PL_PESEL, SG_NRIC_FIN, SG_UEN, AU_ABN, AU_ACN, AU_TFN, AU_MEDICARE, IN_PAN, IN_AADHAAR, FI_PERSONAL_IDENTITY_CODE, KR_RRN, TH_TNIN

## Language Codes

en (English), es (Spanish), fr (French), de (German), it (Italian), pt (Portuguese), nl (Dutch), he (Hebrew), ru (Russian), pl (Polish), zh (Chinese), ja (Japanese), ko (Korean), ar (Arabic), th (Thai), fi (Finnish)

## Common Patterns

### Complete Pipeline
```python
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

results = analyzer.analyze(text=text, language='en')
anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
```

### With Custom Operators
```python
operators = {
    "PERSON": OperatorConfig("replace", {"new_value": "<NAME>"}),
    "EMAIL_ADDRESS": OperatorConfig("mask", {"chars_to_mask": 5}),
    "CREDIT_CARD": OperatorConfig("hash", {"hash_type": "sha256"}),
}
anonymized = anonymizer.anonymize(text=text, analyzer_results=results, operators=operators)
```

### Filtered Analysis
```python
# Only detect specific entities
results = analyzer.analyze(
    text=text,
    entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN"],
    language='en'
)
```

### With Allowlist
```python
results = analyzer.analyze(
    text=text,
    allow_list=["support@company.com", "John Public"],
    language='en'
)
```

### Image to Redacted Image
```python
from PIL import Image
from presidio_image_redactor import ImageRedactorEngine

image = Image.open("input.png")
engine = ImageRedactorEngine()
redacted = engine.redact(image, fill="background")
redacted.save("output.png")
```
