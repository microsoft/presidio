from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DePassportRecognizer(PatternRecognizer):
    """
    Recognize German Reisepassnummer (Passport number) using regex and checksum.

    German passport numbers since 2007 follow these rules:
    - 9 characters alphanumeric
    - First character is a letter (C, F, G, H, J, K)
    - Contains a check digit

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    """

    # Pattern source: https://www.bsi.bund.de/EN/Themen/Oeffentliche-Verwaltung/Elektronische-Identitaeten/Elektronische-Ausweisdokumente/Elektronischer-Reisepass/elektronischer-reisepass_node.html
    PATTERNS = [
        Pattern(
            "Passport (new format since 2007)",
            r"\b[CFGHJK][CFGHJKLMNPRTVWXYZ0-9]{8}\b",
            0.2,
        ),
        Pattern(
            "Passport (generic alphanumeric)",
            r"\b[A-Z0-9]{9}\b",
            0.05,
        ),
    ]

    CONTEXT = [
        "reisepass",
        "reisepassnummer",
        "passnummer",
        "passport",
        "passport number",
        "german passport",
        "deutscher reisepass",
        "pass-nr",
        "passnr",
        "pass"
    ]

    # Character values for checksum calculation
    CHAR_VALUES = {
        "0": 0, "1": 1, "2": 2, "3": 3, "4": 4,
        "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
        "A": 10, "B": 11, "C": 12, "D": 13, "E": 14,
        "F": 15, "G": 16, "H": 17, "I": 18, "J": 19,
        "K": 20, "L": 21, "M": 22, "N": 23, "O": 24,
        "P": 25, "Q": 26, "R": 27, "S": 28, "T": 29,
        "U": 30, "V": 31, "W": 32, "X": 33, "Y": 34,
        "Z": 35,
    }

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_PASSPORT",
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
        """Validate the format and checksum of the German passport number."""
        pattern_text = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        ).upper()

        if len(pattern_text) != 9:
            return False

        # German passport uses forbidden characters: A, B, D, E, I, O, Q, S, U
        # Check this FIRST to reject common German words (DIAGNOSEN, SCHMERZEN, etc.)
        forbidden_chars = set("ABDEIOQSU")
        if any(c in forbidden_chars for c in pattern_text):
            return False

        # Check first character is valid passport prefix
        valid_prefixes = {"C", "F", "G", "H", "J", "K"}
        if pattern_text[0] not in valid_prefixes:
            return None  # Could still be valid older format, use pattern score

        return self._validate_checksum(pattern_text)

    def _validate_checksum(self, passport_number: str) -> bool:
        """
        Validate checksum using weighted sum algorithm.

        The check digit is calculated using weights 7, 3, 1 repeating.
        """
        weights = [7, 3, 1]
        total = 0

        for i, char in enumerate(passport_number[:-1]):
            value = self.CHAR_VALUES.get(char, -1)
            if value == -1:
                return False
            total += value * weights[i % 3]

        check_digit = total % 10
        expected_check = self.CHAR_VALUES.get(passport_number[-1], -1)

        return check_digit == expected_check
