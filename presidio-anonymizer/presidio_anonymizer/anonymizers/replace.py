"""Replaces the PII text entity with new string."""
from presidio_anonymizer.anonymizers import Anonymizer


# TODO implement + test
# TODO need to add here if there is not new value to do <TYPE> - 2543
class Replace(Anonymizer):
    """Receives new text to replace old PII text entity with."""

    def anonymize(self, original_text=None, params={}):
        """:return: new_value."""
        new_val = params.get("new_value")
        if not new_val:
            return f"<{params.get('entity_type')}>"
        return new_val
