from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DeKvnrRecognizer(PatternRecognizer):
    """
    Recognize German KVNR (Krankenversichertennummer) using regex and checksum.

    The KVNR is the lifelong health insurance number for all German residents:
    - 10 characters total
    - Format: [Letter][9 digits]
    - Position 1: One uppercase letter A-Z (no umlauts)
    - Positions 2-9: Eight random digits
    - Position 10: Check digit (modified Luhn algorithm)

    The KVNR is THE primary patient identifier in German healthcare and appears
    in virtually every clinical document (ePA, e-prescriptions, discharge letters).

    Legal basis: §290 SGB V
    Issuing authority: ITSG (Informationstechnische Servicestelle der GKV)

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    """

    # Pattern source: https://www.gkv-datenaustausch.de/kvnr/kvnr.jsp
    PATTERNS = [
        Pattern(
            "KVNR (standard format)",
            r"\b[A-Z][0-9]{9}\b",
            0.4,
        ),
        Pattern(
            "KVNR (with spaces)",
            r"\b[A-Z]\s?[0-9]{3}\s?[0-9]{3}\s?[0-9]{3}\b",
            0.3,
        ),
    ]

    CONTEXT = [
        "krankenversichertennummer",
        "kvnr",
        "versichertennummer",
        "versicherten-nummer",
        "health insurance number",
        "insurance number",
        "patient id",
        "patienten-id",
        "patientennummer",
        "versicherte",
        "krankenkasse",
    ]

    # Letter to number conversion (A=01, B=02, ..., Z=26)
    LETTER_VALUES = {
        "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9,
        "J": 10, "K": 11, "L": 12, "M": 13, "N": 14, "O": 15, "P": 16, "Q": 17,
        "R": 18, "S": 19, "T": 20, "U": 21, "V": 22, "W": 23, "X": 24, "Y": 25,
        "Z": 26,
    }

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_KVNR",
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

    def validate_result(self, pattern_text: str) -> bool:
        """
        Validate the KVNR using format and checksum validation.

        Uses modified Luhn algorithm with weights 1-2-1-2-1-2-1-2-1-2.

        :param pattern_text: Text detected as pattern by regex
        :return: True if valid KVNR, False otherwise
        """
        pattern_text = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        ).upper()

        if len(pattern_text) != 10:
            return False

        # First character must be a letter (A-Z)
        if not pattern_text[0].isalpha():
            return False

        # Remaining 9 characters must be digits
        if not pattern_text[1:].isdigit():
            return False

        # Validate checksum using modified Luhn algorithm
        return self._validate_checksum(pattern_text)

    def _validate_checksum(self, kvnr: str) -> bool:
        """
        Validate KVNR checksum using modified Luhn algorithm.

        Algorithm (§290 SGB V):
        1. Convert letter to 2-digit number (A=01, B=02, ..., Z=26)
        2. This creates an 11-digit number
        3. Multiply digits alternately by 1 and 2 (weights: 1-2-1-2-1-2-1-2-1-2-1)
        4. Calculate cross-sum of each product
        5. Sum all cross-sums
        6. Check digit = last digit of sum (mod 10)

        :param kvnr: The KVNR string (10 characters)
        :return: True if checksum valid, False otherwise
        """
        # Convert letter to 2-digit number
        letter_value = self.LETTER_VALUES.get(kvnr[0], 0)
        if letter_value == 0:
            return False

        # Build 11-digit string: [2 digits from letter][9 digits from KVNR]
        full_number = f"{letter_value:02d}" + kvnr[1:]

        # Weights: 1-2-1-2-1-2-1-2-1-2-1
        weights = [1, 2] * 6  # Creates [1,2,1,2,1,2,1,2,1,2,1,2]
        weights = weights[:11]  # Take first 11

        total = 0
        for i, digit_char in enumerate(full_number):
            digit = int(digit_char)
            product = digit * weights[i]

            # Calculate cross-sum (digit sum) of the product
            # For numbers < 10, cross-sum = number itself
            # For numbers >= 10, sum the digits (e.g., 14 -> 1+4 = 5)
            cross_sum = sum(int(d) for d in str(product))
            total += cross_sum

        # Check digit is the last digit of the total sum
        calculated_check_digit = total % 10
        expected_check_digit = int(kvnr[9])

        return calculated_check_digit == expected_check_digit
