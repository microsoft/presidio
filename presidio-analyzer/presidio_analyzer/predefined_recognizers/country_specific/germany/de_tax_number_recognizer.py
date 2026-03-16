from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DeTaxNumberRecognizer(PatternRecognizer):
    """
    Recognizes German Steuernummer using regex.

    The Steuernummer is a tax number assigned by the local Finanzamt (tax office)
    to individuals and businesses. Unlike the Steueridentifikationsnummer, it can
    change (e.g., upon moving to a different Finanzamt district).

    Legal basis: § 139a Abgabenordnung (AO).
    Data protection: DSGVO Art. 4 Nr. 1 (personenbezogene Daten), BDSG.

    Formats:
        - ELSTER unified (bundeseinheitlich, 13 digits):
            BB FFF UUUUU P  →  2-digit Bundesland code (01–16) + 11 digits
            Example: 2181508150X → normalised as 02181508150X
        - State-specific human-readable (with slashes/spaces):
            NW:  123/4567/8901  (3/4/4 digits)
            BY:  123/456/78901  (3/3/5 digits)
            BE:  12/345/67890   (2/3/5 digits)
            HH:  12/345/67890   (2/3/5 digits)
        - 10-digit plain format (older): XXXXXXXXXX

    Bundesland codes (ELSTER):
        01=SH, 02=HH, 03=NI, 04=HB, 05=NW, 06=HE, 07=RP,
        08=BW, 09=BY, 10=SL, 11=BE, 12=BB, 13=MV, 14=SN, 15=ST, 16=TH

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Steuernummer ELSTER (bundeseinheitlich, 13-stellig)",
            r"\b(0[1-9]|1[0-6])\d{11}\b",
            0.5,
        ),
        Pattern(
            "Steuernummer mit Schrägstrich (Bayern/BW: 3/3/5)",
            r"(?<!\w)\d{3}/\d{3}/\d{5}(?!\w)",
            0.4,
        ),
        Pattern(
            "Steuernummer mit Schrägstrich (NW: 3/4/4 oder allgemein 2-3/3-4/4-5)",
            r"(?<!\w)\d{2,3}/\d{3,4}/\d{4,5}(?!\w)",
            0.2,
        ),
    ]

    CONTEXT = [
        "steuernummer",
        "steuer-nr",
        "steuer nr",
        "st.-nr",
        "st-nr",
        "finanzamt",
        "umsatzsteuer",
        "einkommensteuer",
        "körperschaftsteuer",
        "gewerbesteuer",
        "steuerveranlagung",
        "steuerbescheid",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_TAX_NUMBER",
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
