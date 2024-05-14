from presidio_analyzer import Pattern, PatternRecognizer
from typing import Optional, List, Tuple
import re

class ESPassportNumber(PatternRecognizer):
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
            "ESPassportNumber (Medium)",
            r"\b[A-Z\d]{2}[A-Z\d]?\d{6}\b",
            0.4,
        ),
    ]

    CONTEXT = [
        "passport#",
        "passport #",
        "passportid",
        "passports",
        "passportno",
        "passport no",
        "passportnumber",
        "passport number",
        "passportnumbers",
        "passport numbers",
        
        "libreta pasaporte",
        "número pasaporte",
        "españa pasaporte",
        "números de pasaporte",
        "número de pasaporte",
        "números pasaporte",
        "pasaporte no",
        "Passeport n°",
        "n° Passeport",
        "pasaporte no.",
        "pasaporte n°",
        "spain passport",

        "date of issue",
        "date of expiry"
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "ES_PASSPORT_NUMBER",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        regex_flags = re.IGNORECASE
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
            global_regex_flags=regex_flags
        )
