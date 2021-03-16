""""Result item from the /decrypt method."""
from presidio_anonymizer.entities.engine.result.engine_result_item import \
    EngineResultItem


class DecryptResultItem(EngineResultItem):
    """Information about the decrypted entity."""

    def __init__(
            self,
            start: int,
            end: int,
            entity_type: str,
            decrypted_text: str,
    ):
        """Create DecryptedEntity.

        :param start: start index in the decrypted text.
        :param end: end index in the decrypted text.
        :param decrypted_text: the PII decrypted text.
        """
        self.start = start
        self.end = end
        self.decrypted_text = decrypted_text
        self.entity_type = entity_type

    def __eq__(self, other: 'DecryptResultItem') -> bool:
        return self.start == other.start \
               and self.end == other.end \
               and self.entity_type == other.entity_type \
               and self.decrypted_text == other.decrypted_text

    def get_operated_text(self):
        return self.decrypted_text
