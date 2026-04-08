from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DeBsnrRecognizer(PatternRecognizer):
    r"""
    Recognizes German Betriebsstättennummer (BSNR).

    The BSNR is a 9-digit practice / site-of-care number assigned by the
    regional Kassenärztliche Vereinigung (KV) to each approved practice
    location (Betriebsstätte) participating in the German statutory health
    insurance system.  It appears in billing records, treatment documents, and
    statutory healthcare communications and reveals the treating facility,
    making it sensitive under DSGVO.

    Legal basis: § 75 Abs. 7 SGB V (Sozialgesetzbuch Fünftes Buch).
    Standard: KBV-Richtlinie nach § 75 Abs. 7 SGB V zur Vergabe der Arzt-,
    Betriebsstätten-, Praxisnetz- sowie der Netzverbundnummern.
    Data protection: DSGVO Art. 9 (Gesundheitsdaten), BDSG § 22.

    Format (9 digits):
        Pos 1–2:  KV-Bereichskennzeichen (regional KV code, e.g. 02 Hamburg,
                  06 Nordrhein, 14 Berlin)
        Pos 3–9:  Laufende Nummer (sequential number assigned by KV)

    Examples (fictitious): 021234568, 061789045, 141234567

    Accuracy note: The BSNR has no public checksum, so the 9-digit pattern
    ``\\b\\d{9}\\b`` is inherently broad.  Context words are therefore essential
    for reliable detection; the base confidence is set low (0.2) to prevent
    false positives in digits-only contexts.  Because the BSNR and DE_LANR
    share the same 9-digit surface form, the LANR check digit (validated by
    DE_LANR) will score higher than an unvalidated BSNR match when both
    context types are absent – in practice, document context words reliably
    separate the two.  Formal accuracy evaluation has not been performed on a
    labelled dataset.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Betriebsstättennummer BSNR (9 digits)",
            r"\b\d{9}\b",
            0.2,
        ),
    ]

    CONTEXT = [
        "betriebsstättennummer",
        "betriebsstätten-nummer",
        "bsnr",
        "betriebsstätte",
        "praxisnummer",
        "arztpraxis",
        "praxis",
        "kassenärztliche vereinigung",
        "kv-nummer",
        "kv nummer",
        "praxisadresse",
        "praxisstandort",
        "nebenbetriebsstätte",
        "hauptbetriebsstätte",
        "behandlungsort",
        "vertragsarztpraxis",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_BSNR",
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
