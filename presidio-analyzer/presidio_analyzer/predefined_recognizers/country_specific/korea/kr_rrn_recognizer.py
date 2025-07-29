from typing import List, Optional, Tuple, Union

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class KrRrnRecognizer(PatternRecognizer):
    """
    Recognize Korean Resident Registration Number (RRN).

    The Korean Resident Registration Number (RRN) is
    a 13-digit number issued to all Korean residents.

    The format is YYMMDD-GHIJKLX where:
    - YYMMDD represents the birth date
    - G determines gender and century of birth

    For RRNs issued before October 2020:
    - HIJKL is a serial number assigned by district
    - X is a check digit calculated using the preceding 12 digits

    For RRNs issued after October 2020:
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
            "RRN (Medium)",
            r"\b\d{2}(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])(-?)\d{7}\b",
            0.5,
        )
    ]

    CONTEXT = [
        "Korean RRN",
        "Korean Resident Registration Number",
        "Resident Registration Number",
        "RRN",
        "rrn",
        "rrn#",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "kr",
        supported_entity: str = "KR_RRN",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
    ):
        self.replacement_pairs = replacement_pairs if replacement_pairs else [("-", "")]

        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str) -> Union[bool, None]:
        """
        Validate the pattern logic e.g., by running checksum on a detected pattern.

        This validation is only for RRNs issued before October 2020.
        Therefore, it returns None, not False, at the end of the method.

        :param pattern_text: the text to validated.
        Only the part in text that was detected by the regex engine
        :return: A bool or None, indicating whether the validation was successful.
        """
        # Pre-processing before validation checks
        sanitized_value = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        )

        # Check if the sanitized value has the correct length (13 digits)
        if len(sanitized_value) != 13:
            return False

        # Check if all characters are digits
        if not sanitized_value.isdigit():
            return False

        # Validate region code (HI) and checksum (X)
        region_code = int(sanitized_value[7:9])  # HI
        if self._validate_region_code(region_code) and self._validate_checksum(
            sanitized_value
        ):
            return True

        return None

    def _validate_region_code(self, region_code: int) -> bool:
        """
        Validate the region code of Korean RRN.

        :param region_code: The region code to validate
        :return: True if region code is valid, False otherwise
        """
        return True if 0 <= region_code <= 95 else False

    def _validate_checksum(self, rrn: str) -> bool:
        """
        Validate the checksum of Korean RRN.

        The checksum is calculated using the preceding 12 digits.
        X = (11 - (2A+3B+4C+5D+6E+7F+8G+9H+2I+3J+4K+5L) mod 11) mod 10

        :param rrn: The RRN to validate
        :return: True if checksum is valid, False otherwise
        """

        digit_sum = (
            2 * int(rrn[0])
            + 3 * int(rrn[1])
            + 4 * int(rrn[2])
            + 5 * int(rrn[3])
            + 6 * int(rrn[4])
            + 7 * int(rrn[5])
            + 8 * int(rrn[6])
            + 9 * int(rrn[7])
            + 2 * int(rrn[8])
            + 3 * int(rrn[9])
            + 4 * int(rrn[10])
            + 5 * int(rrn[11])
        )
        checksum = (11 - (digit_sum % 11)) % 10

        return checksum == int(rrn[12])
