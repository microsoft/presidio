"""Replaces the PII text entity with new string."""
from presidio_anonymizer.anonymizers import Anonymizer


# TODO implement + test
# TODO need to add here if there is not new value to do <TYPE> - 2543
class Replace(Anonymizer):
    """Receives new text to replace old PII text entity with."""

    def anonymize(self, params={}):
        """:return: new_val."""
        new_val = params.get("new_value")
        return new_val
