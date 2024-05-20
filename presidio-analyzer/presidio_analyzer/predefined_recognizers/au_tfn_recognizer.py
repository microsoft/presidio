from typing import List, Optional, Tuple

from presidio_analyzer import Pattern, PatternRecognizer


class AuTfnRecognizer(PatternRecognizer):
    """
    Recognizes Australian Tax File Numbers ("TFN").

    The tax file number (TFN) is a unique identifier
    issued by the Australian Taxation Office
    to each taxpaying entity — an individual, company,
    superannuation fund, partnership, or trust.
    The TFN consists of a nine digit number, usually
    presented in the format NNN NNN NNN.
    TFN includes a check digit for detecting erroneous
    number based on simple modulo 11.
    This recognizer uses regex, context words,
    and checksum to identify TFN.
    Reference: https://www.ato.gov.au/individuals/tax-file-number/

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
            "TFN (Medium)",
            r"\b\d{3}\s\d{3}\s\d{3}\b",
            0.1,
        ),
        Pattern(
            "TFN (Low)",
            r"\b\d{9}\b",
            0.01,
        ),
    ]

    CONTEXT = [
        "tax file number",
        "tfn",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "AU_TFN",
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
        tfn_list = [int(digit) for digit in text if not digit.isspace()]

        # Set weights based on digit position
        weight = [1, 4, 3, 7, 5, 8, 6, 9, 10]

        # Perform checksums
        sum_product = 0
        for i in range(9):
            sum_product += tfn_list[i] * weight[i]
        remainder = sum_product % 11
        return remainder == 0

    @staticmethod
    def __sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text
