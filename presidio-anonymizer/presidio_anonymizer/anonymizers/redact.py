"""Replaces the PII text entity with empty string."""
from presidio_anonymizer.anonymizers import Anonymizer


# TODO implement + test
class Redact(Anonymizer):
    """Redact the string - empty value."""

    def anonymize(self, text: str = None, params: dict = None) -> str:
        """:return: an empty value."""
        return ""

    def validate(self, params: dict = None) -> None:
        """TODO: [ADO-2545] docstring."""
        pass
