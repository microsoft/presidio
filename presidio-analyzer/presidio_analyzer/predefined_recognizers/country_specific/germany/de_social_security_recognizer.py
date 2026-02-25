from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DeSocialSecurityRecognizer(PatternRecognizer):
    """
    Recognize German Sozialversicherungsnummer (Social Security number) using regex.

    The German Social Security Number (SVNR/Rentenversicherungsnummer) format:
    - 12 characters total
    - Format: BBTTMMJJASSP
      - BB: Area number (Bereichsnummer) - 2 digits
      - TTMMJJ: Birth date (day, month, year) - 6 digits
      - A: First letter of birth surname - 1 letter
      - SS: Serial number - 2 digits
      - P: Check digit - 1 digit

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    """

    # Pattern source: https://www.deutsche-rentenversicherung.de/SharedDocs/Glossareintraege/DE/V/versicherungsnummer.html
    PATTERNS = [
        Pattern(
            "Social Security (standard format)",
            r"\b[0-9]{2}[0-3][0-9][0-1][0-9][0-9]{2}[A-Z][0-9]{3}\b",
            0.3,
        ),
        Pattern(
            "Social Security (with spaces)",
            r"\b[0-9]{2}\s?[0-3][0-9][0-1][0-9][0-9]{2}\s?[A-Z]\s?[0-9]{3}\b",
            0.25,
        ),
    ]

    CONTEXT = [
        "sozialversicherungsnummer",
        "sozialversicherungs-nummer",
        "svnr",
        "sv-nummer",
        "rentenversicherungsnummer",
        "rvnr",
        "versicherungsnummer",
        "social security",
        "social security number",
        "pension insurance number",
    ]

    # Character values for checksum calculation (official: A=01, B=02, ..., Z=26)
    CHAR_VALUES = {
        "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8, "I": 9,
        "J": 10, "K": 11, "L": 12, "M": 13, "N": 14, "O": 15, "P": 16, "Q": 17, "R": 18,
        "S": 19, "T": 20, "U": 21, "V": 22, "W": 23, "X": 24, "Y": 25, "Z": 26,
    }

    # Official checksum weights per VKVV § 2 (Versicherungsnummern-Verordnung)
    CHECKSUM_WEIGHTS = [2, 1, 2, 5, 7, 1, 2, 1, 2, 1, 2, 1]

    # Valid area codes (Bereichsnummern)
    VALID_AREA_CODES = {
        "02", "03", "04", "05", "06", "07", "08", "09",
        "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
        "20", "21", "22", "23", "24", "25", "26", "27", "28", "29",
        "38", "39", "40", "42", "43", "44", "45", "46", "47", "48", "49",
        "50", "51", "52", "53", "54", "55", "56", "57", "58", "59",
        "60", "61", "62", "63", "64", "65", "66", "67", "68", "69",
        "70", "71", "72", "73", "74", "75", "76", "77", "78", "79",
        "80", "81", "82", "83", "84", "85", "86", "87", "88", "89",
    }

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_SOCIAL_SECURITY",
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

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """Validate the German Social Security number format and checksum."""
        pattern_text = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        ).upper()

        if len(pattern_text) != 12:
            return False

        # Validate area code
        area_code = pattern_text[:2]
        if area_code not in self.VALID_AREA_CODES:
            return False

        # Validate birth date format
        day = pattern_text[2:4]
        month = pattern_text[4:6]

        if not (1 <= int(day) <= 31):
            return False
        if not (1 <= int(month) <= 12):
            return False

        # Validate that position 8 is a letter
        if not pattern_text[8].isalpha():
            return False

        # Validate checksum
        return self._validate_checksum(pattern_text)

    def _validate_checksum(self, svnr: str) -> bool:
        """
        Validate checksum of the German Social Security number per VKVV § 2.

        The check digit is calculated by:
        1. Converting the letter (pos 9) to a two-digit number (A=01, B=02, ..., Z=26)
        2. Creating a 12-digit number from first 11 chars (with letter expanded)
        3. Multiplying each digit by the corresponding weight from CHECKSUM_WEIGHTS
        4. Summing the digit sums (Quersummen) of each product
        5. Check digit = sum mod 10
        """
        # Convert to 12-digit number (letter becomes 2 digits, exclude check digit)
        letter = svnr[8]
        letter_value = self.CHAR_VALUES.get(letter, 0)

        # Build 12-digit string: BBTTMMJJ + letter(2 digits) + SS (exclude check digit P)
        number_str = svnr[:8] + f"{letter_value:02d}" + svnr[9:11]

        # Apply official VKVV weights and sum digit sums (Quersummen)
        total = 0
        for i, char in enumerate(number_str):
            digit = int(char)
            product = digit * self.CHECKSUM_WEIGHTS[i]
            # Add digit sum (Quersumme) of the product (e.g., 14 -> 1 + 4 = 5)
            total += product // 10 + product % 10

        check_digit = total % 10
        expected_check = int(svnr[11])

        return check_digit == expected_check
