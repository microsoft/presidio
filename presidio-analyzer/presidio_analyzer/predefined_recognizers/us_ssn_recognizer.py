from presidio_analyzer import Pattern, PatternRecognizer


# pylint: disable=line-too-long,abstract-method
class UsSsnRecognizer(PatternRecognizer):
    """
    Recognizes US Social Security Number (SSN) using regex
    """

    PATTERN_GROUPS = [
        ("SSN (very weak)", r"\b(([0-9]{5})-([0-9]{4})|([0-9]{3})-([0-9]{6}))\b", 0.05),  # noqa E501
        ("SSN (weak)", r"\b[0-9]{9}\b", 0.3),
        ("SSN (medium)", r"\b([0-9]{3})-([0-9]{2})-([0-9]{4})\b", 0.5),
    ]

    CONTEXT = [
        "social",
        "security",
        # "sec", # Task #603: Support keyphrases ("social sec")
        "ssn",
        "ssns",
        "ssn#",
        "ss#",
        "ssid",
    ]

    def __init__(
        self,
        pattern_groups=None,
        context=None,
        supported_language="en",
        supported_entity="US_SSN",
    ):
        pattern_groups = pattern_groups if pattern_groups else self.PATTERN_GROUPS
        context = context if context else self.CONTEXT
        patterns = [Pattern(*pattern_group) for pattern_group in pattern_groups]
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
