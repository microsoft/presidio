# Predefined Recognizers Organization

This directory contains all the predefined recognizers for Presidio Analyzer, organized into logical subfolders for better maintainability and easier contributions.

## Directory Structure

### `country_specific/`
Contains recognizers specific to particular countries or regions:

- **`us/`** - United States recognizers (SSN, Driver License, Bank, ITIN, Passport, ABA Routing)
- **`uk/`** - United Kingdom recognizers (NHS, NINO)
- **`india/`** - India recognizers (Aadhaar, PAN, Passport, Vehicle Registration, Voter ID)
- **`italy/`** - Italy recognizers (Driver License, Fiscal Code, Identity Card, Passport, VAT Code)
- **`australia/`** - Australia recognizers (ABN, ACN, Medicare, TFN)
- **`spain/`** - Spain recognizers (NIE, NIF)
- **`finland/`** - Finland recognizers (Personal Identity Code)
- **`poland/`** - Poland recognizers (PESEL)
- **`singapore/`** - Singapore recognizers (FIN, UEN)

### `generic/`
Contains recognizers for globally applicable patterns:

- Credit Card, Crypto, Date, Email, IBAN, IP Address, Medical License, Phone, URL

### `ner/`
Contains Named Entity Recognition based recognizers:

- SpaCy, Stanza, Transformers, GLiNER, Azure AI Language

## Adding New Recognizers

When contributing a new recognizer:

1. **Country-specific recognizer**: Add to the appropriate country folder under `country_specific/`. If the country doesn't exist, create a new folder.

2. **Generic recognizer**: Add to the `generic/` folder if it applies globally.

3. **NER-based recognizer**: Add to the `ner/` folder if it's based on machine learning models.

4. **Update imports**: Add the new recognizer import to the main `__init__.py` file to maintain backward compatibility.

5. **Update exports**: Add the class name to the `__all__` list in `__init__.py`.

## Backward Compatibility

All existing imports remain functional. The reorganization maintains full backward compatibility:

```python
# These imports continue to work as before
from presidio_analyzer.predefined_recognizers import CreditCardRecognizer
from presidio_analyzer.predefined_recognizers import UsSsnRecognizer
```

## Testing

When adding new recognizers, ensure all existing tests pass and add appropriate tests for new functionality. 