from presidio_analyzer import Pattern, PatternRecognizer
from typing import Optional, List, Tuple

class NZMinistryOfHealthNumber(PatternRecognizer):
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
            "NZMinistryOfHealthNumber (Medium)",
            r"\b[A-HJ-NP-Z]{3}\d{4}\b",
            0.4,
        ),
    ]

    CONTEXT = [
        "NHI",
        "New Zealand",
        "National Health Index",
        "NHI#",
        "National Health Index#"
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "NZ_MINISTRY_OF_HEALTH_NUMBER",
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
        self.range = (7,7)

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
        if len(text) != 7 or not text[:3].isalpha() or not text[3:].isdigit():
            return False

        # Convert letters to numbers: A=1, B=2, ..., Z=26
        numbers = [(ord(char.upper()) - ord('A') + 1) for char in text[:3]]
        weights = [7, 6, 5]
        
        # Calculate weighted sum of the letters
        weighted_sum = sum(weight * number for weight, number in zip(weights, numbers))
        
        # Calculate the checksum digit
        checksum_digit = 11 - (weighted_sum % 11)
        if checksum_digit == 10:
            checksum_digit = 0  # Checksum digit wraps around to 0 if the result is 10
        
        # Compare the calculated checksum to the last digit of the NHI number
        return checksum_digit == int(text[3:])
    
    @staticmethod
    def __sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text