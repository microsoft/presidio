""""Result item from the /anonymizer method."""
from presidio_anonymizer.entities.engine.result import EngineResultItem


class AnonymizeResultItem(EngineResultItem):
    """Information about the anonymized entity."""

    def __init__(
            self,
            start: int,
            end: int,
            anonynmized_text: str,
            entity_type: str,
            anonymizer: str,
    ):
        """Create DecryptedEntity.

        :param start: start index in the anonymized text.
        :param end: end index in the anonymized text.
        :param anonynmized_text: the PII anonymized text.
        """
        self.start = start
        self.end = end
        self.anonymized_text = anonynmized_text
        self.entity_type = entity_type
        self.anonymizer = anonymizer

    def __eq__(self, other: 'AnonymizeResultItem') -> bool:
        return self.start == other.start \
               and self.end == other.end \
               and self.anonymizer == other.anonymizer \
               and self.anonymized_text == other.anonymized_text \
               and self.entity_type == other.entity_type

    def get_operated_text(self):
        return self.anonymized_text
