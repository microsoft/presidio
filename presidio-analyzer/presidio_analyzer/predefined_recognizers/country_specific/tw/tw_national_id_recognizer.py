from typing import List, Optional
from presidio_analyzer.pattern import Pattern
from presidio_analyzer.pattern_recognizer import PatternRecognizer


class TwNationalIdRecognizer(PatternRecognizer):
    """
    Recognizes Taiwan National Identification Number (National ID / Resident Certificate).
    """

    PATTERNS = [
        Pattern(
            "National ID (weak)",
            r"(?<![0-9A-Za-z])(?-i:[A-Z])[1289][0-9]{8}(?![0-9A-Za-z])",
            0.3,
        ),
    ]

    CONTEXT = [
        "身分證",
        "身份證",
        "身分證字號",
        "身分證號碼",
        "國民身分證",
        "統一證號",
        "taiwan id",
        "national id",
        "tw id",
        "identification number",
    ]

    COUNTRY_CODE = "tw"

    def __init__(
        self,
        name: Optional[str] = None,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "TW_NATIONAL_ID",
        **kwargs
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            name=name if name else "TwNationalIdRecognizer",
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            supported_entity=supported_entity,
            **kwargs
        )

    def invalidate_result(self, pattern_text: str) -> bool:
        """
        Validates Taiwan National ID / Resident UI No. using the Modulus-10 checksum algorithm.
        """
        if not pattern_text or len(pattern_text) != 10:
            return True

        # Presidio ignores case by default; strictly reject lowercase starting letters
        if not pattern_text[0].isupper():
            return True

        # Letter to numerical weight conversion mapping
        letter_mapping = {
            "A": 10,
            "B": 11,
            "C": 12,
            "D": 13,
            "E": 14,
            "F": 15,
            "G": 16,
            "H": 17,
            "J": 18,
            "K": 19,
            "L": 20,
            "M": 21,
            "N": 22,
            "P": 23,
            "Q": 24,
            "R": 25,
            "S": 26,
            "T": 27,
            "U": 28,
            "V": 29,
            "X": 30,
            "Y": 31,
            "W": 32,
            "Z": 33,
            "I": 34,
            "O": 35,
        }

        first_char = pattern_text[0]
        if first_char not in letter_mapping:
            return True

        letter_code = letter_mapping[first_char]

        # Calculate base weight from the alphabet letter code conversion split
        checksum = (letter_code // 10) + (letter_code % 10) * 9

        # Multiply the remaining digits by weights [8, 7, 6, 5, 4, 3, 2, 1]
        weights = [8, 7, 6, 5, 4, 3, 2, 1]
        for i in range(8):
            checksum += int(pattern_text[i + 1]) * weights[i]

        # Add the final check digit (index 9)
        checksum += int(pattern_text[9])

        # A valid structural national ID must be perfectly divisible by 10
        return checksum % 10 != 0
