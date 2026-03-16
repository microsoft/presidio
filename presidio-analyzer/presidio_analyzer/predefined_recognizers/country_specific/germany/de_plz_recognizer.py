from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DePlzRecognizer(PatternRecognizer):
    """
    Recognizes German postal codes (Postleitzahl, PLZ).

    German postal codes consist of exactly 5 digits in the range 01001–99998,
    assigned by Deutsche Post AG. A PLZ alone is generally not sufficient to
    identify a specific natural person and is therefore not directly personal data
    under DSGVO Art. 4 Nr. 1. However, in combination with other data (e.g., street
    address, name), it contributes to identifying an individual, and in very rural
    areas a single PLZ may cover only a handful of addresses.

    Legal basis: DSGVO Art. 4 Nr. 1 in combination with other address data; BDSG.

    Format:
        5 digits, 01001–99998 (boundary values 01000 and 99999 are excluded).
        Examples: 10115 (Berlin Mitte), 80331 (München), 22085 (Hamburg)

    !! ACCURACY WARNING !!
    The pattern `[0-9]{5}` is extremely generic and will produce a very high number
    of false positives when used without context (e.g., year numbers, prices, order
    IDs, phone number fragments, reference numbers). The base confidence is
    therefore set to 0.05 – the recognizer is only actionable when strong context
    words such as "PLZ", "Postleitzahl" or "Postanschrift" are present nearby.
    This recognizer should only be enabled in pipelines where German address data
    is expected. Formal accuracy evaluation has not been performed on a labelled
    dataset.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    # Regex covers 01001–09999 (leading zero) and 10000–99998.
    # Does NOT match 00000 (not a valid PLZ), 01000, 99999, or 6-digit numbers.
    # Reference: Deutsche Post AG PLZ-Verzeichnis.
    PATTERNS = [
        Pattern(
            "Postleitzahl (5 digits, very low base confidence – context required)",
            r"\b(?!01000\b|99999\b)(0[1-9]\d{3}|[1-9]\d{4})\b",
            0.05,
        ),
    ]

    CONTEXT = [
        "plz",
        "postleitzahl",
        "postanschrift",
        "adresse",
        "wohnort",
        "ort",
        "wohnanschrift",
        "lieferadresse",
        "rechnungsadresse",
        "straße",
        "strasse",
        "hausnummer",
        "postfach",
        "bundesland",
        "gemeinde",
        "stadt",
        "dorf",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_PLZ",
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
