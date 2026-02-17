from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class UkPostcodeRecognizer(PatternRecognizer):
    """
    Recognizes UK postcodes using regex.

    UK postcodes follow strict position-specific letter rules across
    six formats (A9 9AA, A99 9AA, A9A 9AA, AA9 9AA, AA99 9AA, AA9A 9AA)
    plus the special GIR 0AA code.

    Reference: https://en.wikipedia.org/wiki/Postcodes_in_the_United_Kingdom

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "UK Postcode",
            r"\b("
            r"GIR\s?0AA"
            r"|[A-PR-UWYZ][0-9][ABCDEFGHJKPSTUW]?\s?[0-9][ABD-HJLNP-UW-Z]{2}"
            r"|[A-PR-UWYZ][0-9]{2}\s?[0-9][ABD-HJLNP-UW-Z]{2}"
            r"|[A-PR-UWYZ][A-HK-Y][0-9][ABEHMNPRVWXY]?\s?[0-9][ABD-HJLNP-UW-Z]{2}"
            r"|[A-PR-UWYZ][A-HK-Y][0-9]{2}\s?[0-9][ABD-HJLNP-UW-Z]{2}"
            r")\b",
            0.1,
        ),
    ]

    CONTEXT = [
        "postcode",
        "post code",
        "postal code",
        "zip",
        "address",
        "delivery",
        "mailing",
        "shipping",
        "correspondence",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "UK_POSTCODE",
        name: Optional[str] = None,
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            name=name,
        )
