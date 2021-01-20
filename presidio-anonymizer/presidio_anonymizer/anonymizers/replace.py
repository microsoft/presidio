"""Replaces the PII text entity with new string."""
from presidio_anonymizer.anonymizers.anonymizer import Anonymizer


# TODO implement + test
class Replace(Anonymizer):
    """Receives new text to replace old PII text entity with."""

    def __init__(self,
                 new_text: str):
        self.new_text = new_text

    def anonymize(self):
        """:return: new_text."""
        pass
