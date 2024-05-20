from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer

# Weak pattern: all FIN number start with "S", "T", "F", "G" or "M"
# and ends with a character, e.g., S2740116C
# Ref: https://en.wikipedia.org/wiki/National_Registration_Identity_Card


class SgFinRecognizer(PatternRecognizer):
    """
    Recognize SG FIN/NRIC number using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern("Nric (weak)", r"(?i)(\b[A-Z][0-9]{7}[A-Z]\b)", 0.3),
        Pattern("Nric (medium)", r"(?i)(\b[STFGM][0-9]{7}[A-Z]\b)", 0.5),
    ]

    CONTEXT = ["fin", "fin#", "nric", "nric#"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "SG_NRIC_FIN",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
