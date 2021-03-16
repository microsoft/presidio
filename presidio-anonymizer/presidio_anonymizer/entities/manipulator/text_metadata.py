class TextMetadata:
    def __init__(
            self,
            start: int,
            end: int,
            entity_type: str,
    ):
        """Create DecryptedEntity.

        :param start: start index in the decrypted text.
        :param end: end index in the decrypted text.
        """
        self.start = start
        self.end = end
        self.entity_type = entity_type

    def __gt__(self, other):
        return self.end > other.end

    def __eq__(self, other):
        return self.start == other.start \
               and self.end == other.end \
               and self.entity_type == other.entity_type

