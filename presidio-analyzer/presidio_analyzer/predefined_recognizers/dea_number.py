from presidio_analyzer import Pattern, PatternRecognizer
from typing import Optional, List, Tuple

class DrugEnforcementAgencyNumber(PatternRecognizer):
    """
    
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
            "DrugEnforcementAgencyNumber (Medium)",
            r"\b[AaBbFfGgMmPpRrXx][A-Za-z]\d{6}[0-9]\b",
            0.4,
        ),
    ]

    CONTEXT = [
        "dea",
        "dea#",
        "drug enforcement administration",
        "drug enforcement agency"
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "DEA_NUMBER",
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

        # custom attributes
        self.type = 'alphanumeric'
        self.range = (9,9)

    def validate_result(self, pattern_text: str) -> bool:
        """
        Validate the pattern logic e.g., by running checksum on a detected pattern.

        :param pattern_text: the text to validated.
        Only the part in text that was detected by the regex engine
        :return: A bool indicating whether the validation was successful.
        """
        # Pre-processing before validation checks
        text = self.__sanitize_value(pattern_text, self.replacement_pairs)
        
        # Validate the format first
        if len(text) != 9 or not text[:2].isalpha() or not text[2:].isdigit():
            return False

        # Extract the numeric digits for checksum calculation
        digits = text[2:-1]
        check_digit = int(text[-1])

        # Calculate the check digit
        sum1 = sum(int(digits[i]) for i in [0, 2, 4])  # Sum of 1st, 3rd, 5th digits
        sum2 = sum(int(digits[i]) for i in [1, 3, 5])  # Sum of 2nd, 4th, 6th digits
        calculated_check_digit = (sum1 + 2 * sum2) % 10

        return calculated_check_digit == check_digit
    
    @staticmethod
    def __sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text