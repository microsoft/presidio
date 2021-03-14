class DecryptedEntity:
    """Information about the decrypted entity."""

    def __init__(
            self,
            entity_type: str,
            start: int,
            end: int,
            decrypted_text: str,
    ):
        """Create DecryptedEntity.

        :param entity_type: type of the PII entity.
        :param start: start index in the decrypted text.
        :param end: end index in the decrypted text.
        :param decrypted_text: the PII decrypted text.
        """
        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.decrypted_text = decrypted_text

    def __eq__(self, other) -> bool:
        """Verify two instances are equal.

        :param other: the other instance to compare.
        :return true if the two instances are equal, false otherwise.
        """

        return (
                self.entity_type == other.entity_type
                and self.start == other.start
                and self.end == other.end
                and self.decrypted_text == other.decrypted_text
        )  # noqa: E127
