from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DeIdCardRecognizer(PatternRecognizer):
    """
    Recognizes German national ID card numbers (Personalausweisnummern) using regex.

    The German Personalausweis (nPA – neuer Personalausweis) has been issued since
    November 2010. Its document number (Seriennummer/Dokumentennummer) is printed on
    the front of the card and encoded in the Machine Readable Zone (MRZ).

    Legal basis: Personalausweisgesetz (PAuswG), Personalausweisverordnung (PAuswV).
    Data protection: DSGVO Art. 4 Nr. 1 (personenbezogene Daten), BDSG.

    Format (nPA, since November 2010):
        - 9 alphanumeric characters (uppercase letters and digits)
        - Character set: letters A–Z (excluding ambiguous chars I, O, Q, S, U)
          and digits 0–9, per ICAO Doc 9303 / BSI TR-03110
        - Example: L01X00T47, T22000129

    Format (old Personalausweis, before November 2010):
        - Letter T followed by 8 digits
        - Example: T22000129

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Personalausweisnummer nPA (Strict ICAO charset, 9 chars)",
            r"\b[CFGHJKLMNPRTVWXYZ][CFGHJKLMNPRTVWXYZ0-9]{7}[CFGHJKLMNPRTVWXYZ0-9]\b",
            0.4,
        ),
        Pattern(
            "Personalausweisnummer alt (T + 8 Ziffern)",
            r"\bT\d{8}\b",
            0.5,
        ),
        Pattern(
            "Personalausweisnummer (Relaxed, 9 alphanumeric)",
            r"\b[A-Z][A-Z0-9]{8}\b",
            0.15,
        ),
    ]

    CONTEXT = [
        "personalausweis",
        "ausweis",
        "personalausweisnummer",
        "ausweisnummer",
        "ausweisdokument",
        "dokumentennummer",
        "seriennummer",
        "npa",
        "neuer personalausweis",
        "personalausweisgesetz",
        "pauwsg",
        "bundespersonalausweis",
        "identity card",
        "national id",
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
