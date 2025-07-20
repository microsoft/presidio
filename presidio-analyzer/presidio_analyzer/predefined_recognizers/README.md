# Predefined Recognizers Organization

This directory contains all the predefined recognizers for Presidio Analyzer, organized into logical subfolders for better maintainability and easier contributions.

## Directory Structure

- `country_specific/`: Contains recognizers specific to particular countries or regions:
- `generic/`: Contains recognizers for globally applicable patterns:
- `nlp_engine_recognizers/`: Containers recognizers that map to NLP engines
- `ner/`: Contains standalone Named Entity Recognition recognizers:
- `third_party/`: Contains recognizers that integrate with third-party services

## Adding New Recognizers

When contributing a new recognizer:

1. **Country-specific recognizer**: Add to the appropriate country folder under `country_specific/`. If the country doesn't exist, create a new folder.

2. **Generic recognizer**: Add to the `generic/` folder if it applies globally.

3. **NLP Engine-based recognizer**: Add to the `nlp_engine_recognizers/` folder if it's based on machine learning models that work with NLP engines.

4. **Standalone NER recognizer**: Add to the `ner/` folder if it's a standalone NER model.

5. **Third-party service recognizer**: Add to the `third_party/` folder if it integrates with external services.

6. **Update imports**: Add the new recognizer import to the main `__init__.py` file to maintain backward compatibility.

7. **Update exports**: Add the class name to the `__all__` list in `__init__.py`.

## Backward Compatibility

All existing imports remain functional. The reorganization maintains full backward compatibility:

```python
# These imports continue to work as before
from presidio_analyzer.predefined_recognizers import CreditCardRecognizer
from presidio_analyzer.predefined_recognizers import UsSsnRecognizer
```

## Testing

When adding new recognizers, ensure all existing tests pass and add appropriate tests for new functionality.
