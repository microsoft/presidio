from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DePersonalIdRecognizer(PatternRecognizer):
    """
    Recognize German Personalausweisnummer (Personal ID number) using regex and checksum.

    The German ID card number (Personalausweisnummer) has different formats:
    - Old format (before Nov 2010): 10 characters alphanumeric
    - New format (since Nov 2010): 9 characters alphanumeric

    Both formats use a check digit based on the ISO 7064 Mod 97 algorithm variant.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    """

    # Pattern source: https://www.personalausweisportal.de/Webs/PA/EN/citizens/german-id-card/german-id-card-node.html
    PATTERNS = [
        Pattern(
            "Personal ID (new format)",
            r"\b[CFGHJKLMNPRTVWXYZ0-9]{9}\b",
            0.1,
        ),
        Pattern(
            "Personal ID (old format)",
            r"\b[0-9]{10}\b",
            0.05,
        ),
    ]

    CONTEXT = [
        "personalausweis",
        "personalausweisnummer",
        "ausweisnummer",
        "ausweisnnr",
        "identity card",
        "id card",
        "german id",
        "ausweis",
        "identitätskarte",
        "perso",
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
        supported_entity: str = "DE_PERSONAL_ID",
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
        """Validate the checksum of the German Personal ID number."""
        pattern_text = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        ).upper()

        if len(pattern_text) not in (9, 10):
            return False

        # German ID uses forbidden characters: A, E, I, O, U (vowels) and some others
        # Valid characters are: 0-9, C, F, G, H, J, K, L, M, N, P, R, T, V, W, X, Y, Z
        forbidden_chars = set("ABDEIOQSU")
        if any(c in forbidden_chars for c in pattern_text):
            return False

        return self._validate_checksum(pattern_text)

    def _validate_checksum(self, id_number: str) -> bool:
        """
        Validate checksum using weighted sum algorithm.

        The check digit is calculated using weights 7, 3, 1 repeating.
        """
        weights = [7, 3, 1]
        total = 0

        for i, char in enumerate(id_number[:-1]):
            value = self.CHAR_VALUES.get(char, -1)
            if value == -1:
                return False
            total += value * weights[i % 3]

        check_digit = total % 10
        expected_check = self.CHAR_VALUES.get(id_number[-1], -1)

        return check_digit == expected_check
