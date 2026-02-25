from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DeTaxIdRecognizer(PatternRecognizer):
    """
    Recognize German Steueridentifikationsnummer (Tax ID) using regex and checksum.

    The German Tax ID (Steuer-ID) has the following characteristics:
    - 11 digits
    - First digit is not 0
    - One digit appears exactly twice or three times
    - At least one digit appears zero times
    - Last digit is a check digit (ISO 7064 MOD 11,10)

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    """

    # Pattern source: https://www.bzst.de/DE/Privatpersonen/SteuerlicheIdentifikationsnummer/steuerlicheidentifikationsnummer.html
    PATTERNS = [
        Pattern(
            "Tax ID (with separators)",
            r"\b[1-9][0-9]{2}[\s/-]?[0-9]{3}[\s/-]?[0-9]{3}[\s/-]?[0-9]{2}\b",
            0.3,
        ),
        Pattern(
            "Tax ID (continuous)",
            r"\b[1-9][0-9]{10}\b",
            0.2,
        ),
    ]

    CONTEXT = [
        "steueridentifikationsnummer",
        "steuer-id",
        "steuerid",
        "steuer-identifikationsnummer",
        "tax id",
        "tax identification number",
        "idnr",
        "id-nr",
        "tin",
        "steuernummer",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_TAX_ID",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        name: Optional[str] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs
            if replacement_pairs
            else [("-", ""), (" ", ""), ("/", "")]
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

    def validate_result(self, pattern_text: str) -> bool:
        """Validate the German Tax ID using structure and checksum validation."""
        pattern_text = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        )

        if len(pattern_text) != 11:
            return False

        if not pattern_text.isdigit():
            return False

        # First digit cannot be 0
        if pattern_text[0] == "0":
            return False

        # Check digit distribution (one digit appears 2-3 times, one appears 0 times)
        if not self._validate_digit_distribution(pattern_text[:10]):
            return False

        # Validate check digit using ISO 7064 MOD 11,10
        return self._validate_checksum(pattern_text)

    def _validate_digit_distribution(self, digits: str) -> bool:
        """
        Validate that the first 10 digits follow the required distribution.

        Rules:
        - One digit must appear exactly 2 or 3 times
        - At least one digit (0-9) must not appear at all
        """
        from collections import Counter

        digit_counts = Counter(digits)

        # Check that at least one digit doesn't appear
        if len(digit_counts) == 10:
            return False

        # Check that one digit appears 2 or 3 times
        count_values = list(digit_counts.values())
        has_double_or_triple = any(c in (2, 3) for c in count_values)

        return has_double_or_triple

    def _validate_checksum(self, tax_id: str) -> bool:
        """
        Validate checksum using ISO 7064 MOD 11,10 algorithm.
        """
        product = 10

        for digit in tax_id[:10]:
            summe = (int(digit) + product) % 10
            if summe == 0:
                summe = 10
            product = (2 * summe) % 11

        check_digit = (11 - product) % 10
        return check_digit == int(tax_id[10])
