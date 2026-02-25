from typing import List, Optional, Tuple

from presidio_analyzer import EntityRecognizer, Pattern, PatternRecognizer


class DeBsnrRecognizer(PatternRecognizer):
    """
    Recognize German BSNR (Betriebsstättennummer) using regex and validation.

    The BSNR is a facility number that uniquely identifies the location of
    service provision in the German statutory health insurance system:
    - 9 digits total
    - Digits 1-2: KV state/regional association code (see VALID_KV_CODES)
    - Digits 3-7: Facility identifier (assigned by KV)
    - Digits 8-9: Additional digits (often "00" for older BSNRs)

    The BSNR appears in prescriptions, discharge letters, and billing documents,
    identifying the treatment facility. This is quasi-PII as it can narrow down
    where a patient received treatment.

    Legal basis: §75 Abs. 7 SGB V
    Issuing authority: Kassenärztliche Vereinigungen (KV)
    Source: KBV Arztnummern-Richtlinie Anlage 1

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    """

    # Pattern source: https://wiki.hl7.de/index.php/LANR_und_BSNR

    # Valid KV region codes per KBV Arztnummern-Richtlinie Anlage 1
    # Standard KV regions
    VALID_KV_CODES = {
        "01",  # Schleswig-Holstein
        "02",  # Hamburg
        "03",  # Bremen
        "17",  # Niedersachsen
        "20",  # Westfalen-Lippe
        "38",  # Nordrhein
        "46",  # Hessen
        "51",  # Rheinland-Pfalz
        "52",  # Baden-Württemberg
        "71",  # Bayern
        "72",  # Berlin
        "73",  # Saarland
        "74",  # KBV (Kassenärztliche Bundesvereinigung)
        "78",  # Mecklenburg-Vorpommern
        "83",  # Brandenburg
        "88",  # Sachsen-Anhalt
        "93",  # Thüringen
        "98",  # Sachsen
        # Special codes for hospitals (Anlage 8 BMV-Ä)
        "35",  # Krankenhäuser
    }

    PATTERNS = [
        Pattern(
            "BSNR (9 digits)",
            r"\b[0-9]{9}\b",
            0.05,  # Very low score - requires context or valid KV code
        ),
        Pattern(
            "BSNR (with context)",
            r"(?i)(?:bsnr|betriebsstättennummer|betriebsstaetten-nr|betriebsstätten-nr)[\s:]*([0-9]{9})\b",
            0.5,
        ),
    ]

    CONTEXT = [
        "bsnr",
        "betriebsstättennummer",
        "betriebsst\u00e4ttennummer",  # With umlaut
        "betriebsstaetten-nr",
        "betriebsst\u00e4tten-nr",  # With umlaut
        "facility number",
        "praxis",
        "praxisnummer",
        "behandlungsort",
        "einrichtung",
        "klinik",
        "krankenhaus",
        "behandlungsstelle",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_BSNR",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
        name: Optional[str] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [("-", ""), (" ", ""), (".", "")]
        )
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            name=name,
        )

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """
        Validate the BSNR format using KV regional code validation.

        Validates that the first 2 digits match a valid KV region code
        per KBV Arztnummern-Richtlinie Anlage 1.

        :param pattern_text: Text detected as pattern by regex
        :return: True if valid KV code, False if invalid, None if uncertain
        """
        pattern_text = EntityRecognizer.sanitize_value(
            pattern_text, self.replacement_pairs
        )

        if len(pattern_text) != 9:
            return False

        if not pattern_text.isdigit():
            return False

        # Basic validation: BSNR should not be all zeros
        if pattern_text == "000000000":
            return False

        # Validate KV regional code (digits 1-2)
        kv_code = pattern_text[:2]
        if kv_code in self.VALID_KV_CODES:
            # Valid KV code - increase confidence
            return True

        # Unknown KV code - could be valid (historic or special cases)
        # but reduce confidence by returning None
        return None
