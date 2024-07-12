from presidio_analyzer import Pattern, PatternRecognizer
from typing import Optional, List, Tuple
import re

class SWIFTCode(PatternRecognizer):
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
            "SWIFTCode (Weak)",
            r"\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?\b",
            0.3,
        ),
    ]

    CONTEXT = [
        "international organization for standardization 9362",
        "iso 9362",
        "iso9362",
        "swift#",
        "swiftcode",
        "swiftnumber",
        "swiftroutingnumber",
        "swift code",
        "swift number #",
        "swift routing number",
        "bic number",
        "bic code",
        "bic #",
        "bic#",
        "bank identifier code",
        "Organisation internationale de normalisation 9362",
        "rapide #",
        "code SWIFT",
        "le numéro de swift",
        "swift numéro d'acheminement",
        "le numéro BIC",
        "# BIC",
        "code identificateur de banque",
        "SWIFTコード",
        "SWIFT番号",
        "BIC番号",
        "BICコード",
        "SWIFT コード",
        "SWIFT 番号",
        "BIC 番号",
        "BIC コード",
        "金融機関識別コード",
        "金融機関コード",
        "銀行コード"
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "SWIFT_CODE",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        regex_flags = re.IGNORECASE
    ):
        
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            global_regex_flags=regex_flags
        )

        # custom attributes
        self.type = 'alphanumeric'
        self.range = (8,11)