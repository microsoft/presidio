from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DeLanrRecognizer(PatternRecognizer):
    """
    Recognize German LANR (Lebenslange Arztnummer) using regex and validation.

    The LANR is a lifelong physician number for doctors participating in the
    German statutory health insurance system:
    - 9 digits total
    - Digits 1-6: Unique physician identifier (lifetime)
    - Digit 7: Check digit (Prüfziffer)
    - Digits 8-9: Specialty group code (Fachgruppenschlüssel)

    The LANR appears in prescriptions, discharge letters, and billing documents,
    identifying the treating physician. This is PII as it indirectly identifies
    the treating physician, which can reveal sensitive information about the
    patient's condition.

    Legal basis: §75 Abs. 7 SGB V
    Issuing authority: Kassenärztliche Bundesvereinigung (KBV)

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    """

    # Pattern source: https://hub.kbv.de/display/BASE1X0/NamingSystems
    PATTERNS = [
        Pattern(
            "LANR (9 digits)",
            r"\b[0-9]{9}\b",
            0.1,  # Low score due to overlap with other 9-digit numbers
        ),
        Pattern(
            "LANR (with context)",
            r"(?i)(?:lanr|arztnummer|arzt-nr)[\s:]*([0-9]{9})\b",
            0.5,
        ),
    ]

    CONTEXT = [
        "lanr",
        "lebenslange arztnummer",
        "arztnummer",
        "arzt-nr",
        "arzt-nummer",
        "physician number",
        "doctor number",
        "behandelnder arzt",
        "verschreibender arzt",
        "arzt",
        "dr.",
        "dr. med.",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_LANR",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        name: Optional[str] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [("-", ""), (" ", ""), (".", "")]
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

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """
        Validate the LANR format and checksum.

        The LANR checksum algorithm (Position 7) per KBV specification:
        1. Multiply first 6 digits alternately by 4 and 9
        2. Sum the products
        3. Take modulo 10
        4. Subtract from 10 → check digit (if result is 10, check digit is 0)

        Source: KBV Richtlinie nach §75 Abs. 7 SGB V

        :param pattern_text: Text detected as pattern by regex
        :return: True if valid, False if invalid
        """
        pattern_text = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        )

        if len(pattern_text) != 9:
            return False

        if not pattern_text.isdigit():
            return False

        # Basic validation: LANR should not be all zeros
        if pattern_text == "000000000":
            return False

        return self._validate_checksum(pattern_text)

    def _validate_checksum(self, lanr: str) -> bool:
        """
        Validate LANR checksum at position 7.

        Algorithm:
        - Multiply digits 1-6 alternately by 4 and 9
        - Sum all products
        - Check digit = (10 - (sum mod 10)) mod 10

        :param lanr: The 9-digit LANR string
        :return: True if checksum valid, False otherwise
        """
        weights = [4, 9, 4, 9, 4, 9]
        total = 0

        for i in range(6):
            total += int(lanr[i]) * weights[i]

        calculated_check_digit = (10 - (total % 10)) % 10
        expected_check_digit = int(lanr[6])

        return calculated_check_digit == expected_check_digit
