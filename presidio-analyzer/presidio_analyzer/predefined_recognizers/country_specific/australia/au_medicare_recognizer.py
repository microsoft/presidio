from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class AuMedicareRecognizer(PatternRecognizer):
    """
    Recognizes Australian Medicare number using regex, context words, and checksum.

    Medicare number is a unique identifier issued by Australian Government
    that enables the cardholder to receive a rebates of medical expenses
    under Australia's Medicare system.
    It uses a modulus 10 checksum scheme to validate the number.
    Reference: https://en.wikipedia.org/wiki/Medicare_card_(Australia)


    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    This can allow a greater variety in input, for example by removing dashes or spaces.
    """

    PATTERNS = [
        Pattern(
            "Australian Medicare Number (Medium)",
            r"\b[2-6]\d{3}\s\d{5}\s\d\b",
            0.1,
        ),
        Pattern(
            "Australian Medicare Number (Low)",
            r"\b[2-6]\d{9}\b",
            0.01,
        ),
    ]

    CONTEXT = [
        "medicare",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "AU_MEDICARE",
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
        text = EntityRecognizer.sanitize_value(pattern_text, self.replacement_pairs)
        medicare_list = [int(digit) for digit in text if not digit.isspace()]

        # Set weights based on digit position
        weight = [1, 3, 7, 9, 1, 3, 7, 9]

        # Perform checksums
        sum_product = 0
        for i in range(8):
            sum_product += medicare_list[i] * weight[i]
        remainder = sum_product % 10
        return remainder == medicare_list[8]
