from typing import List, Optional, Tuple

from presidio_analyzer import Pattern
from presidio_analyzer.predefined_recognizers.country_specific.korea.kr_rrn_recognizer import (  # noqa: E501
    KrRrnRecognizer,
)


class KrFrnRecognizer(KrRrnRecognizer):
    """
    Recognize Korean Foreigner Registration Number (FRN).

    The Korean FRN is a 13-digit number issued to registered foreigners in Korea.
    The format is YYMMDD-GHIJKLX where:
    - YYMMDD represents the birth date.
    - G determines gender and century (5-8).
        - 5: Male, 1900-1999 birth
        - 6: Female, 1900-1999 birth
        - 7: Male, 2000-2099 birth
        - 8: Female, 2000-2099 birth
        - (Note: 9 and 0 are sometimes used for 1800s birth, but rare)

    For FRNs issued before October 2020:
    - HIJKL is a serial number assigned by district
    - X is a check digit calculated using the preceding 12 digits

    For FRNs issued after October 2020:
    - HIJKLX is a random number

    Reference: https://en.wikipedia.org/wiki/Resident_registration_number

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    This can allow a greater variety in input, for example by removing dashes.
    """

    PATTERNS = [
        Pattern(
            "FRN (Medium)",
            r"(?<!\d)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])(-?)[5-8]\d{6}(?!\d)",
            0.5,
        )
    ]

    CONTEXT = [
        "외국인등록번호",
        "Korean FRN",
        "FRN",
        "Foreigner Registration Number",
        "Korean Foreigner Registration Number",
        "외국인번호",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "ko",
        supported_entity: str = "KR_FRN",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        name: Optional[str] = None,
    ):
        super().__init__(
            patterns=patterns if patterns else self.PATTERNS,
            context=context if context else self.CONTEXT,
            supported_language=supported_language,
            supported_entity=supported_entity,
            replacement_pairs=replacement_pairs,
            name=name,
        )

    def _validate_checksum(self, frn: str) -> bool:
        """
        Validate the checksum of Korean FRN.

        The checksum is calculated using the preceding 12 digits.
        X = (13 - (2A+3B+4C+5D+6E+7F+8G+9H+2I+3J+4K+5L) mod 11) mod 10

        :param frn: The FRN to validate
        :return: True if checksum is valid, False otherwise
        """
        digit_sum = super()._compute_checksum(frn)
        checksum = (13 - (digit_sum % 11)) % 10
        return checksum == int(frn[12])
