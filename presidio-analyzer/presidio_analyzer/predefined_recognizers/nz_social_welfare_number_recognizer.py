from presidio_analyzer import Pattern, PatternRecognizer
from typing import Optional, List, Tuple

class NZSocialWelfareNumberRecognizer(PatternRecognizer):
    """
    Recognizes New Zealand Social Welfare Numbers using regex.
    
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
            "NzSocialWelfareNumber (Weak)",
            r"\b\d{3}[-]?\d{3}[-]?\d{3}\b",
            0.4,
        ),
    ]

    CONTEXT = [
        "social welfare #",
        "social welfare#",
        "social welfare No.",
        "social welfare number",
        "swn#"
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "NZ_SWN",
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
        self.range = (9,11)
    
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
        if len(text) != 9 or not text.isdigit():
            return False
        
        # Extract digits (assuming no separators like spaces or hyphens)
        digits = [int(d) for d in text if d.isdigit()]

        # Checksum calculation (Luhn Algorithm)
        checksum = 0
        for i, digit in enumerate(digits[:-1]):
            weight = 1 if i % 2 else 3  # Alternate weighting
            product = digit * weight
            checksum += product // 10 + product % 10

        return (checksum + digits[-1]) % 10 == 0  # Check if checksum digit matches
    
    @staticmethod
    def __sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text