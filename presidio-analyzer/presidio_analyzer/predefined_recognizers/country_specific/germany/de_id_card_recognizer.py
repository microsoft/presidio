from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DeIdCardRecognizer(PatternRecognizer):
    """
    Recognizes German ID card numbers (Personalausweisnummer).

    The post-2010 German ID card number is a 9-character alphanumeric
    string. The first character is a letter from the set
    [L, M, N, P, R, T, V, W, X, Y], followed by 8 alphanumeric
    characters (digits 0-9 and letters C, F, G, H, J, K,
    L, M, N, P, R, T, V, W, X, Y — no vowels, no B, D, S, Q, I, O, Z).

    Reference: https://en.wikipedia.org/wiki/German_identity_card

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "ID Card (very weak)",
            r"\b[LMNPRTVWXY][CFGHJKLMNPRTVWXY0-9]{8}\b",
            0.01,
        ),
    ]

    CONTEXT = [
        "personalausweis",
        "personalausweisnummer",
        "ausweis",
        "ausweisnummer",
        "identity card",
        "id card",
        "ausweisdokument",
        "identitatsnachweis",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_ID_CARD",
        name: Optional[str] = None,
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            name=name,
        )
