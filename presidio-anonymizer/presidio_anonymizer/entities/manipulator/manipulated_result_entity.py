class ManipulatedEntity:
    """Information about the anonymized entity."""

    def __init__(
        self,
        manipulator: str,
        entity_type: str,
        start: int,
        end: int,
        manipulated_text: str,
    ):
        """Create AnonymizerResult.

        :param manipulator: name of the anonymizer.
        :param entity_type: type of the PII entity.
        :param start: start index in the anonymized text.
        :param end: end index in the anonymized text.
        :param manipulated_text: the PII anonymized text.
        """
        self.manipulator = manipulator
        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.manipulated_text = manipulated_text

    def __eq__(self, other) -> bool:
        """Verify two instances are equal.

        :param other: the other instance to compare.
        :return true if the two instances are equal, false otherwise.
        """

        return (
                self.manipulator == other.manipulator
                and self.entity_type == other.entity_type
                and self.start == other.start
                and self.end == other.end
                and self.manipulated_text == other.manipulated_text
        )  # noqa: E127
