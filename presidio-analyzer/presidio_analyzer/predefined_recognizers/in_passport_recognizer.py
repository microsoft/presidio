from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class InPassportRecognizer(PatternRecognizer):
    """
    Recognizes Indian Passport Number.

    Indian Passport Number is a eight digit alphanumeric number.

    Reference:
    https://www.bajajallianz.com/blog/travel-insurance-articles/where-is-passport-number-in-indian-passport.html

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "PASSPORT",
            r"\b[A-Z][1-9][0-9]{2}[0-9]{4}[1-9]\b",
            0.1,
        ),
    ]

    CONTEXT = ["passport", "indian passport", "passport number"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "IN_PASSPORT",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
