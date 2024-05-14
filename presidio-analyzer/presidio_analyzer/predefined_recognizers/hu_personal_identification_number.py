from presidio_analyzer import Pattern, PatternRecognizer
from typing import Optional, List, Tuple

class HUPersonalIdentificationNumber(PatternRecognizer):
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
            "HUPersonalIdentificationNumber (Medium)",
            r"\b(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{4}\b",
            0.4,
        ),
    ]

    CONTEXT = [
        "id number",
        "identification number",
        "sz ig",
        "sz. ig.",
        "sz.ig.",
        "személyazonosító igazolvány",
        "személyi igazolvány"
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "HU_PERSONAL_IDENTIFICATION_NUMBER",
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
        
        # Check that the full number is the correct length
        if len(text) != 11 or not text.isdigit():
            return False

        # Weights for the checksum calculation
        weights = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]  
        total = sum(int(digit) * weight for digit, weight in zip(text[:-1], weights))

        checksum_calculated = total % 11
        checksum_digit = int(text[-1])

        # Check if the calculated checksum matches the last digit
        return checksum_calculated == checksum_digit and checksum_calculated != 10
    
    @staticmethod
    def __sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text