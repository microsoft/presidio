from presidio_analyzer import Pattern, PatternRecognizer


class UsPhoneRecognizer(PatternRecognizer):
    """
    Recognizes US Phone numbers using regex
    """

    PATTERNS = [
        Pattern(
            "Phone (strong)",
            r"(\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|d{3}[-\.\s]\d{3}[-\.\s]\\d{4})",
            0.7,
        ),
        Pattern("Phone (medium)", r"\b(\d{3}[-\.\s]\d{3}[-\.\s]??\d{4})\b", 0.5),
        Pattern("Phone (weak)", r"(\b\d{10}\b)", 0.05),
    ]

    # pylint: disable=line-too-long,abstract-method
    CONTEXT = ["phone", "number", "telephone", "cell", "mobile", "call"]

    def __init__(
        self,
        patterns=None,
        context=None,
        supported_language="en",
        supported_entity="PHONE_NUMBER",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
