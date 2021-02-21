"""Replaces the PII text entity with empty string."""
from typing import Dict

from presidio_anonymizer.anonymizers import Anonymizer


class Redact(Anonymizer):
    """Redact the string - empty value."""

    def anonymize(self, text: str = None, params: Dict = None) -> str:
        """:return: an empty value."""
        return ""

    def validate(self, params: Dict = None) -> None:
        """Redact does not require any paramters so no validation is needed."""
        pass

    def anonymizer_name(self) -> str:
        """Return anonymizer name."""
        return "redact"
