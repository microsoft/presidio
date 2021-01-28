"""Replaces the PII text entity with empty string."""
from presidio_anonymizer.anonymizers import Anonymizer


class Redact(Anonymizer):
    """Redact the string - empty value."""

    def anonymize(self, original_text, params):
        """:return: an empty value."""
        return ""
