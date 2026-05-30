from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class PhPhilhealthRecognizer(PatternRecognizer):
    """
    Recognizes Philippine Health Insurance Corporation PhilHealth numbers.

    The PhilHealth Identification Number (PIN) is a 12-digit identifier
    commonly written in 2-9-1 format:
    - 12 digits without separators (e.g., 120000157266)
    - 2 digits + hyphen + 9 digits + hyphen + 1 digit
      (e.g., 12-000015726-6)

    Reference:
    - PhilHealth Electronic Claims Implementation Guide v3.1 states that
      pPIN is a 12-digit PhilHealth Identification Number and that the last
      character is a modulus 11 check digit. The guide is published under
      philhealth.gov.ph/downloads/eclaims/.
    - Forcepoint DLP classifier documentation publishes 12-000015726-6 as a
      valid PhilHealth Identification Number example. The weighted modulus 11
      check used here validates that public example.
    - Check digit convention: compute 11 - (weighted total mod 11), map 11 to
      0, and reject 10 because it cannot be represented as a single decimal
      digit. This follows the standard single-digit modulus 11 handling also
      used by ISO/IEC 7064 Mod 11,10 identifiers.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    COUNTRY_CODE = "ph"

    PATTERNS = [
        Pattern(
            "PhilHealth PIN (formatted)",
            r"(?<!\d)\d{2}-\d{9}-\d(?!\d)",
            0.5,
        ),
        Pattern(
            "PhilHealth PIN (unformatted)",
            r"(?<!\d)\d{12}(?!\d)",
            0.1,
        ),
    ]

    CONTEXT = [
        "philhealth",
        "philhealth number",
        "philhealth no",
        "philhealth no.",
        "philhealth id",
        "philhealth identification number",
        "philhealth pin",
        "health insurance",
        "member data record",
        "philhealth mdr",
        "kalusugan",
        "seguro",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "PH_HEALTH_INSURANCE",
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
        Check if the pattern text cannot be validated as a PhilHealth PIN.

        The public PhilHealth documentation confirms a modulus 11 check digit
        but does not publish a full algorithm. This implementation uses the
        common 2..12 weighted modulus 11 convention, which validates the public
        Forcepoint example 12-000015726-6. It maps a computed check value of
        11 to 0 and rejects 10 because 10 cannot be represented as a single
        decimal digit.

        :param pattern_text: Text detected as pattern by regex
        :return: True if invalidated
        """
        digits = self._normalize(pattern_text)
        return not self._is_valid_pin(digits)

    @staticmethod
    def _normalize(pattern_text: str) -> str:
        return "".join(c for c in pattern_text if c.isdigit())

    @classmethod
    def _is_valid_pin(cls, digits: str) -> bool:
        if len(digits) != 12 or not digits.isdigit():
            return False

        weights = range(2, 13)
        total = sum(int(digit) * weight for digit, weight in zip(digits[:11], weights))
        check_digit = 11 - (total % 11)

        if check_digit == 11:
            check_digit = 0
        elif check_digit == 10:
            return False

        return check_digit == int(digits[-1])
