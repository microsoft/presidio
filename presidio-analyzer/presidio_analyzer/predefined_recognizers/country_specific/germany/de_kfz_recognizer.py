from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DeKfzRecognizer(PatternRecognizer):
    """
    Recognizes German vehicle registration plates (KFZ-Kennzeichen).

    German license plates are issued by local Zulassungsbehörden (vehicle registration
    authorities). While not exclusively personal (vehicles can be owned by companies),
    they can be linked to natural persons and are considered personally identifiable
    information in the context of data protection law.

    Legal basis: Fahrzeug-Zulassungsverordnung (FZV) § 8, § 9.
    Data protection: DSGVO Art. 4 Nr. 1 (personenbezogene Daten) – license plates
    constitute personal data when they can be linked to an identifiable person (ECJ
    ruling C-582/14, Breyer v. Germany).

    Format:
        [Unterscheidungszeichen] [Erkennungszeichen] [Ziffern] [Suffix]

        Unterscheidungszeichen: 1–3 uppercase letters (district/city code)
        Erkennungszeichen:      1–2 uppercase letters
        Ziffern:               1–4 digits
        Suffix (optional):     E (electric vehicle) or H (Oldtimer/historic, ≥30 years)

    Examples
            B AB 1234      (Berlin)
            M XY 999       (München)
            HH AB 1234     (Hamburg)
            KA EF 1H       (Karlsruhe, historic)
            MIL E 1234E    (Miltenberg, electric)
            S AB 12        (Stuttgart)

    Note: Seasonal plates (Saison-Kennzeichen) also contain month ranges but are not
    covered by this pattern.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "KFZ-Kennzeichen (mit Leerzeichen)",
            r"\b[A-ZÄÖÜ]{1,3}\s[A-Z]{1,2}\s\d{1,4}[EH]?\b",
            0.3,
        ),
        Pattern(
            "KFZ-Kennzeichen (mit Bindestrich)",
            r"\b[A-ZÄÖÜ]{1,3}-[A-Z]{1,2}-\d{1,4}[EH]?\b",
            0.3,
        ),
        Pattern(
            "KFZ-Kennzeichen (ASCII only, mit Leerzeichen)",
            r"\b[A-Z]{1,3}\s[A-Z]{1,2}\s\d{1,4}[EH]?\b",
            0.2,
        ),
    ]

    CONTEXT = [
        "kennzeichen",
        "kfz-kennzeichen",
        "kraftfahrzeugkennzeichen",
        "nummernschild",
        "fahrzeugkennzeichen",
        "zulassung",
        "kfz",
        "fahrzeug",
        "auto",
        "pkw",
        "lkw",
        "fahrzeugschein",
        "fahrzeugbrief",
        "zulassungsbescheinigung",
        "amtliches kennzeichen",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_KFZ",
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
