from presidio_analyzer import Pattern, PatternRecognizer
from typing import Optional, List, Tuple

class HkIdentityCardRecognizer(PatternRecognizer):
    """
    Recognizes Hong Kong Identity Card numbers using regex.
    
    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    This can allow a greater variety in input, for example by removing dashes or spaces.
    """

    PATTERNS = [
        Pattern(
            "HkIdentityCard (Medium)",
            r"(?<![\w\d])[A-Z]{1,2}\d{6}(?:\([0-9A]\)|[0-9A])(?![\w\d])",
            0.4,
        ),
    ]

    CONTEXT = [
        "hkid",
        "hong kong identity card",
        "HKIDC",
        "id card",
        "identity card",
        "hk identity card",
        "hong kong id",
        "香港身份證",
        "香港永久性居民身份證",
        "身份證",
        "身份証",
        "身分證",
        "身分証",
        "香港身份証",
        "香港身分證",
        "香港身分証",
        "香港身份證",
        "香港居民身份證",
        "香港居民身份証",
        "香港居民身分證",
        "香港居民身分証",
        "香港永久性居民身份証",
        "香港永久性居民身分證",
        "香港永久性居民身分証",
        "香港永久性居民身份證",
        "香港非永久性居民身份證",
        "香港非永久性居民身份証",
        "香港非永久性居民身分證",
        "香港非永久性居民身分証",
        "香港特別行政區永久性居民身份證",
        "香港特別行政區永久性居民身份証",
        "香港特別行政區永久性居民身分證",
        "香港特別行政區永久性居民身分証",
        "香港特別行政區非永久性居民身份證",
        "香港特別行政區非永久性居民身份証",
        "香港特別行政區非永久性居民身分證",
        "香港特別行政區非永久性居民身分証",
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "HK_IDENTITY_NUMBER",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
    ):
        
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

        # custom attributes
        self.type = 'alphanumeric'
        self.range = (8,11)
