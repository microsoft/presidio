from presidio_analyzer import Pattern, PatternRecognizer


class UsPhoneRecognizer(PatternRecognizer):
    """
    Recognizes US Phone numbers using regex
    """

    PATTERN_GROUPS = [
        (
            "Phone (strong)",
            r"(\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|d{3}[-\.\s]\d{3}[-\.\s]\\d{4})",
            0.7,
        ),
        ("Phone (medium)", r"\b(\d{3}[-\.\s]\d{3}[-\.\s]??\d{4})\b", 0.5),
        ("Phone (weak)", r"(\b\d{10}\b)", 0.05),
    ]

    # pylint: disable=line-too-long,abstract-method
    CONTEXT = ["phone", "number", "telephone", "cell", "mobile", "call"]

    def __init__(
        self,
        pattern_groups=None,
        context=None,
        supported_language="en",
        supported_entity="PHONE_NUMBER",
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
