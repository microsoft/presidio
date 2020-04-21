from presidio_analyzer import Pattern, PatternRecognizer


class NhsRecognizer(PatternRecognizer):
    """
    Recognizes NHS number using regex and checksum
    """

    PATTERN_GROUPS = [
        ("NHS (medium)", r"\b([0-9]{3})[- ]?([0-9]{3})[- ]?([0-9]{4})\b", 0.5,),
    ]

    CONTEXT = [
        "national health service",
        "nhs",
        "health services authority",
        "health authority",
    ]

    def __init__(
        self,
        pattern_groups=None,
        context=None,
        supported_language="en",
        supported_entity="UK_NHS",
        replacement_pairs=[("-", ""), (" ", "")],
    ):
        self.replacement_pairs = replacement_pairs
        context = context if context else self.CONTEXT
        pattern_groups = pattern_groups if pattern_groups else self.PATTERN_GROUPS
        patterns = [Pattern(*pattern_group) for pattern_group in pattern_groups]
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text):
        text = self.__sanitize_value(pattern_text, self.replacement_pairs)
        total = sum(
            [int(c) * multiplier for c, multiplier in zip(text, reversed(range(11)))]
        )
        remainder = total % 11
        check_remainder = remainder == 0

        return check_remainder

    @staticmethod
    def __sanitize_value(text, replacement_pairs):
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text
