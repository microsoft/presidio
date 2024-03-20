from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer

class APIKeyRecognizer(PatternRecognizer):
    """
    Recognizes API Keys using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "API Key",
            (
                r"\b(?i)([A-Za-z0-9]{20,40}|[A-Za-z0-9]{6}-[A-Za-z0-9]{6}-[A-Za-z0-9]{6})\b"
            ),
            0.2 # low confidence
        ),
    ]
    CONTEXT = ["api", "api key", "token", "secret", "access key", "access_token"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "API_KEY",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )