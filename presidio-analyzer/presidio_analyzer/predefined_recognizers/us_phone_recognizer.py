from typing import Optional, List

from presidio_analyzer import Pattern, PatternRecognizer


class UsPhoneRecognizer(PatternRecognizer):
    """
    Recognizes US Phone numbers using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Phone (strong)",
            r"(\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]\d{3}[-\.\s]\d{4})",
            0.7,
        ),
        Pattern("Phone (medium)", r"\b(\d{3}[-\.\s]\d{3}[-\.\s]??\d{4})\b", 0.5),
        Pattern("Phone (weak)", r"(\b\d{10}\b)", 0.05),
    ]

    CONTEXT = ["phone", "number", "telephone", "cell", "cellphone", "mobile", "call"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "PHONE_NUMBER",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
