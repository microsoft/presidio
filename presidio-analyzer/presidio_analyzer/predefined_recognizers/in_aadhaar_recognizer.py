from typing import List, Optional, Tuple

from presidio_analyzer import Pattern, PatternRecognizer
from presidio_analyzer.analyzer_utils import PresidioAnalyzerUtils as Utils


class InAadhaarRecognizer(PatternRecognizer):
    """
    Recognizes Indian UIDAI Person Identification Number ("AADHAAR").

    Reference: https://en.wikipedia.org/wiki/Aadhaar
    A 12 digit unique number that is issued to each individual by Government of India
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
            "AADHAAR (Very Weak)",
            r"\b[0-9]{12}\b",
            0.01,
        ),
    ]

    CONTEXT = [
        "aadhaar",
        "uidai",
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "IN_AADHAAR",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs
            if replacement_pairs
            else [("-", ""), (" ", ""), (":", "")]
        )
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str) -> bool:
        """Determine absolute value based on calculation."""
        sanitized_value = Utils.sanitize_value(pattern_text, self.replacement_pairs)
        return self.__check_aadhaar(sanitized_value)

    def __check_aadhaar(self, sanitized_value: str) -> bool:
        is_valid_aadhaar: bool = False
        if (
            len(sanitized_value) == 12
            and sanitized_value.isnumeric() is True
            and int(sanitized_value[0]) >= 2
            and Utils.is_verhoeff_number(int(sanitized_value)) is True
            and Utils.is_palindrome(sanitized_value) is False
        ):
            is_valid_aadhaar = True
        return is_valid_aadhaar
