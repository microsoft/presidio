"""Recognizer for US National Provider Identifier (NPI)."""

from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class UsNpiRecognizer(PatternRecognizer):
    """Recognize US National Provider Identifier (NPI) using regex + checksum.

    The NPI is a unique 10-digit number assigned to healthcare providers in the
    United States by CMS (Centers for Medicare & Medicaid Services). It is a
    HIPAA-mandated identifier that appears on insurance claims, prescriptions,
    and provider directories.

    Format:
    - Exactly 10 digits
    - Starts with 1 (Type 1, individual) or 2 (Type 2, organization)
    - Last digit is a Luhn check digit (using "80840" prefix per CMS spec)

    Reference: https://www.cms.gov/Regulations-and-Guidance/Administrative-Simplification/NationalProvIdentStand

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    This can allow a greater variety in input, for example by removing dashes or
    spaces.
    """

    PATTERNS = [
        Pattern(
            "NPI (weak)",
            r"\b[12]\d{9}\b",
            0.1,
        ),
        Pattern(
            "NPI (medium)",
            r"\b[12]\d{3}[ -]\d{3}[ -]\d{3}\b",
            0.4,
        ),
    ]

    CONTEXT = [
        "npi",
        "national provider",
        "provider",
        "npi number",
        "provider id",
        "provider identifier",
        "taxonomy",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "US_NPI",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        name: Optional[str] = None,
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
            name=name,
        )

    def validate_result(self, pattern_text: str) -> bool:  # noqa: D102
        sanitized_value = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        )
        return self.__npi_luhn_checksum(sanitized_value)

    def invalidate_result(self, pattern_text: str) -> bool:  # noqa: D102
        sanitized_value = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        )
        # Reject degenerate patterns where all body digits are identical
        # (e.g., 1111111111 or 1111111112 where the last digit is a check digit).
        if sanitized_value:
            body = sanitized_value[:-1] if len(sanitized_value) > 1 else sanitized_value
            if body and len(set(body)) == 1:
                return True
        return False

    @staticmethod
    def __npi_luhn_checksum(sanitized_value: str) -> bool:
        """Validate NPI using Luhn algorithm with "80840" prefix per CMS spec.

        Steps:
        1. Take the 10-digit NPI
        2. Prepend "80840" to get a 15-digit number
        3. Apply standard Luhn algorithm: result mod 10 should equal 0
        """
        prefixed = "80840" + sanitized_value
        digits = [int(d) for d in prefixed]

        # Standard Luhn: from rightmost digit, double every second digit
        checksum = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                doubled = digit * 2
                checksum += doubled - 9 if doubled > 9 else doubled
            else:
                checksum += digit

        return checksum % 10 == 0
