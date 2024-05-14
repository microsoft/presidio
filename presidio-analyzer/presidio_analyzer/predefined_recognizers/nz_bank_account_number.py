from presidio_analyzer import Pattern, PatternRecognizer
from typing import Optional, List, Tuple

class NZBankAccountNumber(PatternRecognizer):
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
            "NZBankAccountNumber (Medium)",
            r"\b\d{2}[- ]?\d{3,4}[- ]?\d{7}[- ]?\d{2,3}\b",
            0.4,
        ),
    ]

    CONTEXT = [
        "account number",
        "bank account",
        "bank_acct_id",
        "bank_acct_branch",
        "bank_acct_nbr"
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "NZ_BANK_ACCOUNT_NUMBER",
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
        if len(text) not in [15, 16] or not text.isdigit():
            return False
        
        # Define weights based on the NZ bank account validation algorithm
        weights = [0, 0, 6, 3, 7, 9, 10, 5, 8, 4, 2, 1]  # For bank, branch, and base account number
        if len(text) == 15:
            weights.extend([11, 0])
        elif len(text) == 16:
            weights.extend([11, 0, 0])
        
        # Apply weights and sum the products
        total = sum(int(num) * weight for num, weight in zip(text, weights))
        
        # Check if the total modulo 11 is 0
        return total % 11 == 0
    
    @staticmethod
    def __sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text