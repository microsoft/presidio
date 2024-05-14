from typing import List, Optional, Tuple

from presidio_analyzer import Pattern, PatternRecognizer


class ABARoutingNumber(PatternRecognizer):
    """

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    This can allow a greater variety in input, for example by removing dashes or spaces.
    """  # noqa: D205

    PATTERNS = [
        Pattern(
            "ABARoutingNumber (Medium)",
            r"\b(0[1-9]|1[0-2]|2[1-9]|3[0-2]|6[1-9]|7[0-2]|80)\d{2}[- ]?\d{4}[- ]?\d\b",
            0.4,
        ),
    ]

    CONTEXT = [
        "aba number",
        "aba#",
        "aba",
        "abarouting#",
        "abaroutingnumber",
        "americanbankassociationrouting#",
        "americanbankassociationroutingnumber",
        "bankrouting#",
        "bankroutingnumber",
        "routing #",
        "routing no",
        "routing number",
        "routing transit number",
        "routing#",
        "RTN"
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "ABA_ROUTING_NUMBER",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
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
        )

    def validate_result(self, pattern_text: str) -> bool:
        """
        Validate the pattern logic e.g., by running checksum on a detected pattern.

        :param pattern_text: the text to validated.
        Only the part in text that was detected by the regex engine
        :return: A bool indicating whether the validation was successful.
        """
        # Pre-processing before validation checks
        text = self.__sanitize_value(pattern_text, self.replacement_pairs)

        if len(text) != 9 or not text.isdigit():
            return False  # Routing number must contain exactly 9 digits

        weights = [3, 7, 1]  # ABA weights
        total = 0

        # Sum the products of the digits and their corresponding weights
        for i in range(8):  # Only the first 8 digits are used in the calculation
            total += int(text[i]) * weights[i % 3]

        # Check if the sum mod 10 plus the last digit equals 10 (or the sum mod 10 is 0 if the last digit is 0)
        return (total + int(text[8])) % 10 == 0

    @staticmethod
    def __sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text
