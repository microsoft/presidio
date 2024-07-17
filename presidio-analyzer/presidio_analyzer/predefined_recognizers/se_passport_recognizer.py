from presidio_analyzer import Pattern, PatternRecognizer
from typing import Optional, List, Tuple

class SePassportRecognizer(PatternRecognizer):
    """
    Recognizes Swedish passport numbers using regex.
    
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
            "SsPassport (Medium)",
            r"\b[0-9]{8}\b",
            0.1,
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
        
        "alien registration card",
        "g3 processing fees",
        "multiple entry",
        "Numéro de passeport",
        "passeport n °",
        "passeport non",
        "passeport #",
        "passeport#",
        "passeportnon",
        "passeportn °",
        "passnummer",
        "pass nr",
        "schengen visa",
        "schengen visas",
        "single entry",
        "sverige pass",
        "visa requirements",
        "visa processing",
        "visa type",

        "date of issue",
        "date of expiry"
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "SE_PASSPORT_NUMBER",
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
        self.range = (8,8)
