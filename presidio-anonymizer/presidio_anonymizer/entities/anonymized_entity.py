class AnonymizedEntity:
    """Information about the anonymized entity."""

    def __init__(
        self,
        anonymizer: str,
        entity_type: str,
        start: int,
        end: int,
        anonymized_text: str,
    ):
        """Create AnonymizerResultItem.

        :param anonymizer: name of the anonymizer.
        :param entity_type: type of the PII entity.
        :param start: start index in the anonymized text.
        :param end: end index in the anonymized text.
        :param anonymized_text: the PII anonymized text.
        """
        self.anonymizer = anonymizer
        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.anonymized_text = anonymized_text

    def __eq__(self, other) -> bool:
        """Verify two instances are equal.

        :param other: the other instance to compare.
        :return true if the two instances are equal, false otherwise.
        """

        return (
            self.anonymizer == other.anonymizer
            and self.entity_type == other.entity_type
            and self.start == other.start
            and self.end == other.end
            and self.anonymized_text == other.anonymized_text
        )  # noqa: E127
