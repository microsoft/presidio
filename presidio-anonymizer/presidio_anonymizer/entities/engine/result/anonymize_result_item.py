"""Result item for the /anonymizer method."""
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
        """
        Anonymized text data item.

        :param start: start index of the anonymized text in the general text.
        :param end: end index of the anonymized text in the general text.
        :param anonynmized_text: the text after the anonymization.
        :param entity_type: the entity type of the text.
        :param anonymizer: the name of the anonymizer we used.
        """
        EngineResultItem.__init__(self, start, end, entity_type)
        self.anonymized_text = anonynmized_text
        self.anonymizer = anonymizer

    def __eq__(self, other: 'AnonymizeResultItem') -> bool:
        """Check two objects from this class is equal."""
        return (self.start == other.start
                and self.end == other.end
                and self.anonymizer == other.anonymizer
                and self.anonymized_text == other.anonymized_text
                and self.entity_type == other.entity_type)

    def get_operated_text(self):
        """
        Get the text we performed the operation on.

        :return: the text we operated over and this anonymize result represent.
        """
        return self.anonymized_text
