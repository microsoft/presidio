from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class ItPassportRecognizer(PatternRecognizer):
    """
    Recognizes IT Passport number using case-insensitive regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Passport (very weak)",
            r"(?i)\b[A-Z]{2}\d{7}\b",  # noqa: E501
            0.01,
        ),
    ]

    CONTEXT = [
        "passaporto",
        "elettronico",
        "italiano",
        "viaggio",
        "viaggiare",
        "estero",
        "documento",
        "dogana",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "it",
        supported_entity: str = "IT_PASSPORT",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
