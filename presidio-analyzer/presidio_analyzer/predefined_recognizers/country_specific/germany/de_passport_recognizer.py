from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DePassportRecognizer(PatternRecognizer):
    """
    Recognizes German passport numbers (Reisepassnummern) using regex.

    German passports are issued by the Bundesdruckerei on behalf of the
    Bundesrepublik Deutschland. The document number consists of 9 alphanumeric
    characters and appears on the data page and in the Machine Readable Zone (MRZ).

    Legal basis: Passgesetz (PassG) § 4, Passverordnung (PassV).
    Data protection: DSGVO Art. 4 Nr. 1 (personenbezogene Daten), BDSG.

    Format:
        - 9 alphanumeric characters (uppercase letters from the limited set
          C, F, G, H, J, K, L, M, N, P, R, T, V, W, X, Y, Z and digits 0–9)
        - First character: typically a letter from the series identifier
        - Followed by 8 alphanumeric characters
        - Example: C01X00T47, F20400481

    The character set excludes visually ambiguous characters (I, O, Q, S, U)
    as per ICAO Doc 9303 (Machine Readable Travel Documents) specifications.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Reisepassnummer (Strict ICAO charset)",
            r"\b[CFGHJKLMNPRTVWXYZ][CFGHJKLMNPRTVWXYZ0-9]{7}[0-9]\b",
            0.4,
        ),
        Pattern(
            "Reisepassnummer (Relaxed)",
            r"\b[A-Z][A-Z0-9]{7}[0-9]\b",
            0.2,
        ),
    ]

    CONTEXT = [
        "reisepass",
        "pass",
        "passnummer",
        "reisepassnummer",
        "passport",
        "passport number",
        "pass-nr",
        "dokumentennummer",
        "bundesrepublik deutschland",
        "ausweisdokument",
        "mrz",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_PASSPORT",
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
