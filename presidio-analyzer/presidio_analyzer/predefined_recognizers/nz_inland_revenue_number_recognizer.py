from presidio_analyzer import Pattern, PatternRecognizer
from typing import Optional, List, Tuple

class NzInlandRevenueNumberRecognizer(PatternRecognizer):
    """
    Recognizes New Zealand Inland Revenue numbers using regex.
    
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
            "NzInlandRevenueNumber (Medium)",
            r"\b(?:0[1-9]|[1-9][0-9]|[1-4][0-9]{2}|150)[\s-]?\d{3}[\s-]?\d{3}(?:\d{2})?\b",
            0.5,
        ),
    ]

    CONTEXT = [
        "ird no.",
        "ird no#",
        "nz ird",
        "new zealand ird",
        "ird number",
        "inland revenue number"
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "NZ_INLAND_REVENUE_NUMBER",
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
        self.type = 'numeric'
        self.range = (8,13)

    def validate_result(self, pattern_text: str) -> bool:
        """
        Validate the pattern logic e.g., by running checksum on a detected pattern.

        :param pattern_text: the text to validated.
        Only the part in text that was detected by the regex engine
        :return: A bool indicating whether the validation was successful.
        """
        # Pre-processing before validation checks
        text = self.__sanitize_value(pattern_text, self.replacement_pairs)
        ird_list = [int(digit) for digit in text if not digit.isspace()]
        
        # Validate the length of the IRD number
        if len(text) not in (8, 9):
            return False

        # Define the weights for the IRD number
        weights = [3, 2, 7, 6, 5, 4, 3, 2]
        if len(text) == 9:
            weights.append(0)  # Append 0 for the 9th digit

        # Calculate the sum of the products of weights and corresponding digits
        weighted_sum = sum(val * weights[index] for index, val in enumerate(ird_list))

        # Calculate the remainder
        remainder = weighted_sum % 11

        # Determine validity based on the remainder
        if remainder == 0:
            return True
        else:
            check_digit = 11 - remainder
            # The check digit should match the last digit of the IRD number
            return check_digit == int(text[-1])
    
    @staticmethod
    def __sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text