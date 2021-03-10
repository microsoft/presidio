class AnonymizerResultItem:
    """Anonymizer result item."""

    def __init__(self, anonymizer, entity_type, start, end, anonymized_text):
        """Create AnonymizerResultItem."""
        self.anonymizer = anonymizer
        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.anonymized_text = anonymized_text

    def __eq__(self, other):
        """Verify two instances are equal."""

        return self.anonymizer == other.anonymizer and \
               self.entity_type == other.entity_type and \
               self.start == other.start and \
               self.end == other.end and \
               self.anonymized_text == other.anonymized_text  # noqa: E127
