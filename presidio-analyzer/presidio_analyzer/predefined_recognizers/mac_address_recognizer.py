from typing import Optional, List, Tuple

from presidio_analyzer import Pattern, PatternRecognizer


class BloodGroupRecognizer(PatternRecognizer):
    """
    Recognizes MAC Address using Regex pattern.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    
    PATTERNS = [
        Pattern(
            "MAC Address (high)",
            r"\b[0-9A-Fa-f]{12}\b",
            0.8,
        ),
        Pattern(
            "MAC Address (low)",
            r"\b[0-9A-Za-z]{12}\b",
            0.2,
        )
    ]

    CONTEXT = [
        "MAC address",
        "Media Access Control address",
        "MAC"
    ]




    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "BLOOD_GROUPS",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [(" ", ""), ("-", ""), (".", "")]
        )
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
