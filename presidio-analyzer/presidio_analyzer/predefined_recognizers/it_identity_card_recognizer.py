from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class ItIdentityCardRecognizer(PatternRecognizer):
    """
    Recognizes IT Identity Card number using case-insensitive regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Paper-based Identity Card (very weak)",
            r"(?i)\b[A-Z]{2}\s?\d{7}\b",  # noqa: E501
            0.01,
        ),
        Pattern(
            "Electronic Identity Card (CIE) 2.0 (very weak)",
            r"(?i)\b\d{7}[A-Z]{2}\b",  # noqa: E501
            0.01,
        ),
        Pattern(
            "Electronic Identity Card (CIE) 3.0 (very weak)",
            r"(?i)\b[A-Z]{2}\d{5}[A-Z]{2}\b",  # noqa: E501
            0.01,
        ),
    ]

    CONTEXT = [
        'carta',
        'identità',
        'elettronica',
        'cie',
        'documento',
        'riconoscimento',
        'espatrio'
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "it",
        supported_entity: str = "IT_IDENTITY_CARD",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
