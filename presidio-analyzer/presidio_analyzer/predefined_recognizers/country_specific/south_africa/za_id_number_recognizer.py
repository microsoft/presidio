from datetime import date
from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class ZaIdNumberRecognizer(PatternRecognizer):
    """
    Recognize South African ID numbers using regex and structural validation.

    South African identity numbers are 13 digits in the ``YYMMDD SSSS CAZ``
    layout:
    - ``YYMMDD``: date of birth
    - ``SSSS``: sequence number
    - ``C``: citizenship / status
    - ``A``: typically 8 or 9
    - ``Z``: check digit using the Luhn algorithm

    Reference:
    https://en.wikipedia.org/wiki/South_African_identity_card#Identity_Number

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    COUNTRY_CODE = "za"

    PATTERNS = [
        Pattern(
            "South African ID Number",
            r"\b\d{10}[0-2][89]\d\b",
            0.2,
        ),
    ]

    CONTEXT = [
        "id",
        "identity",
        "identity number",
        "id number",
        "south african id",
        "rsa id",
        "smart id",
        "national id",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "ZA_ID_NUMBER",
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

    def validate_result(self, pattern_text: str) -> bool:  # noqa: D102
        if len(pattern_text) != 13 or not pattern_text.isdigit():
            return False

        if not self._has_valid_birth_date(pattern_text[:6]):
            return False

        if pattern_text[10] not in {"0", "1", "2"}:
            return False

        if pattern_text[11] not in {"8", "9"}:
            return False

        return self._is_luhn_valid(pattern_text)

    @staticmethod
    def _has_valid_birth_date(date_part: str) -> bool:
        month = int(date_part[2:4])
        day = int(date_part[4:6])
        year_suffix = int(date_part[:2])

        for century in (1900, 2000):
            try:
                date(century + year_suffix, month, day)
                return True
            except ValueError:
                continue
        return False

    @staticmethod
    def _is_luhn_valid(value: str) -> bool:
        digits = [int(digit) for digit in value]
        checksum = 0
        parity = len(digits) % 2

        for index, digit in enumerate(digits):
            if index % 2 == parity:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit

        return checksum % 10 == 0
