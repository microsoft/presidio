from typing import List, Optional, Tuple

from presidio_analyzer import Pattern, PatternRecognizer
import re

class UsPassportRecognizer(PatternRecognizer):
    """
    Recognizes US Passport number using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    # Weak pattern: all passport numbers are a weak match, e.g., 14019033
    PATTERNS = [
        Pattern("USPassport (very weak)", r"(\b[0-9]{9}\b)", 0.05),
        Pattern("USPassport Next Generation (very weak)", r"(\b[A-Z][0-9]{8}\b)", 0.1),
        Pattern(
            "USPassportNumber Next Generation (medium)",
            r"\b[A-Z\d]{1}\d{8}\b",
            0.5,
        ),
    ]
    CONTEXT = [
        "passport#",
        "passport #",
        "passportid",
        "passports",
        "passportno",
        "passport no",
        "passportnumber",
        "passport number",
        "passportnumbers",
        "passport numbers",
        
        "amarican passport",
        "us passport",
        "travel",
        "states",
        "american"
        "america"

        "date of issue",
        "date of expiry"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "US_PASSPORT",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        regex_flags = re.IGNORECASE
    ):
        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [("-", ""), (" ", "")]
        )

        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            global_regex_flags=regex_flags
        )

        # custom attributes
        self.type = 'numeric/alphanumeric'
        self.range = (9,9)
