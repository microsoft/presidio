from presidio_analyzer import Pattern, PatternRecognizer


class UsItinRecognizer(PatternRecognizer):
    """
    Recognizes US ITIN (Individual Taxpayer Identification Number) using regex
    """

    # pylint: disable=line-too-long,abstract-method
    PATTERNS = [
        Pattern(
            "Itin (very weak)",
            r"(\b(9\d{2})[- ]{1}((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))(\d{4})\b)|(\b(9\d{2})((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))[- ]{1}(\d{4})\b)",  # noqa: E501
            0.05,
        ),
        Pattern(
            "Itin (weak)",
            r"\b(9\d{2})((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))(\d{4})\b",  # noqa: E501
            0.3,
        ),
        Pattern(
            "Itin (medium)",
            r"\b(9\d{2})[- ]{1}((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))[- ]{1}(\d{4})\b",  # noqa: E501
            0.5,
        ),
    ]

    CONTEXT = ["individual", "taxpayer", "itin", "tax", "payer", "taxid", "tin"]

    def __init__(
        self,
        patterns=None,
        context=None,
        supported_language="en",
        supported_entity="US_ITIN",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
