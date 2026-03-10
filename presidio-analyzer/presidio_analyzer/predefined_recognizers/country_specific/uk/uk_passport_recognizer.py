from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class UkPassportRecognizer(PatternRecognizer):
    """
    Recognizes UK passport numbers using regex.

    UK passports issued from 2015 onwards use a 2-letter prefix
    followed by 7 digits (e.g., AB1234567).

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "UK Passport (weak)",
            r"\b[A-Z]{2}\d{7}\b",
            0.1,
        ),
    ]

    CONTEXT = [
        "passport",
        "passport number",
        "travel document",
        "uk passport",
        "british passport",
        "her majesty",
        "his majesty",
        "hm passport",
        "hmpo",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "UK_PASSPORT",
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
