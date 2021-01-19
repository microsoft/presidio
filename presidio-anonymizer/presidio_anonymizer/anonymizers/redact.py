"""Replaces the PII text entity with empty string."""
from anonymizers.anonymizer import Anonymizer


# TODO implement + test
class Redact(Anonymizer):
    """Redact the string - empty value."""

    def __init__(self):
        pass

    def anonymize(self):
        """:return: an empty value."""
        pass
