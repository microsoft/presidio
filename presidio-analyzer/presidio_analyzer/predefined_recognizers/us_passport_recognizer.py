from presidio_analyzer import Pattern, PatternRecognizer


class UsPassportRecognizer(PatternRecognizer):
    """
    Recognizes US Passport number using regex
    """

    # pylint: disable=line-too-long,abstract-method
    # Weak pattern: all passport numbers are a weak match, e.g., 14019033
    PATTERN_GROUPS = [
        ("Passport (very weak)", r"(\b[0-9]{9}\b)", 0.05),
    ]
    CONTEXT = ["us", "united", "states", "passport", "passport#", "travel", "document"]

    def __init__(
        self,
        pattern_groups=None,
        context=None,
        supported_language="en",
        supported_entity="US_PASSPORT",
    ):
        context = context if context else self.CONTEXT
        pattern_groups = pattern_groups if pattern_groups else self.PATTERN_GROUPS
        patterns = [Pattern(*pattern_group) for pattern_group in pattern_groups]
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
