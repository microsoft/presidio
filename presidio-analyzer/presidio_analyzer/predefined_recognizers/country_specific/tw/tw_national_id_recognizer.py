from typing import List, Optional
from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult

class TwNationalIdRecognizer(PatternRecognizer):
    """Recognize Taiwan National Identification Number using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    COUNTRY_CODE = "tw"

    # Match 1 upper case letter followed by 9 digits
    PATTERNS = [
        Pattern("National ID (weak)", r"\b[A-Z][1289][0-9]{8}\b", 0.3),
    ]

    # Context keywords in English and Traditional Chinese
    CONTEXT = [
        "taiwan id",
        "national id",
        "identity card",
        "身分證",
        "身份證",
        "身分證字號",
        "統一編號",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "zh",
        supported_entity: str = "TW_NATIONAL_ID",
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

    def invalidate_result(self, pattern_text: str) -> bool:
        """
        Check if the pattern text cannot be validated as a TW_NATIONAL_ID entity.

        :param pattern_text: Text detected as pattern by regex
        :return: True if invalidated
        """
        # Presidio uses IGNORECASE by default. Explicitly reject lowercase starting letters.
        if not pattern_text[0].isupper():
            return True
            
        return False
