from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DeLanrRecognizer(PatternRecognizer):
    r"""
    Recognizes German Lebenslange Arztnummer (LANR).

    The LANR is a 9-digit lifetime physician number assigned by the
    Kassenärztliche Vereinigung (KV) to every licensed physician participating
    in the German statutory health insurance system (Vertragsarzt).  It appears
    on prescriptions (Rezepte), billing records, discharge letters, and other
    statutory healthcare documents.

    Legal basis: § 75 Abs. 7 SGB V (Sozialgesetzbuch Fünftes Buch).
    Standard: KBV-Richtlinie nach § 75 Abs. 7 SGB V zur Vergabe der Arzt-,
    Betriebsstätten-, Praxisnetz- sowie der Netzverbundnummern.
    Data protection: DSGVO Art. 9 (Gesundheitsdaten), BDSG § 22.

    Format (9 digits):
        Pos 1–6:  Arztnummer (physician identifier, assigned by KV)
        Pos 7:    Prüfziffer (check digit, derived from pos 1–6)
        Pos 8–9:  Arztgruppe / Fachgruppe (specialty / physician group code)

    Examples (fictitious): 123456901, 234567601, 100000414

    Check digit algorithm (KBV specification):
        1. Apply weights [4, 9, 2, 10, 5, 3] to digits at positions 1–6.
        2. For each product > 9, replace it with the cross-sum of its digits
           (e.g. 18 → 1+8 = 9, 40 → 4+0 = 4).
        3. Sum all six values.
        4. Check digit (pos 7) = sum mod 10.

    Accuracy note: The base pattern ``\\b\\d{9}\\b`` matches any 9-digit token.
    Because LANRs share the same surface form as other 9-digit identifiers
    (e.g. DE_BSNR), the checksum in ``validate_result()`` is the primary guard
    against false positives; context words are required for high-confidence
    results without a valid checksum.  Formal accuracy evaluation has not been
    performed on a labelled dataset.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Lebenslange Arztnummer LANR (9 digits)",
            r"\b\d{9}\b",
            0.3,
        ),
    ]

    CONTEXT = [
        "arztnummer",
        "lanr",
        "lebenslange arztnummer",
        "arzt-nr",
        "arzt nr",
        "arzt-nummer",
        "vertragsarzt",
        "kassenarzt",
        "niedergelassener arzt",
        "kbv",
        "kassenärztliche vereinigung",
        "kv-nummer",
        "rezept",
        "verschreibung",
        "behandelnder arzt",
        "hausarzt",
        "facharzt",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_LANR",
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

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """
        Validate the LANR using the KBV check digit algorithm.

        Algorithm source: KBV-Richtlinie nach § 75 Abs. 7 SGB V.

        :param pattern_text: the text to validate (9 digits)
        :return: True if check digit is valid, False otherwise
        """
        pattern_text = pattern_text.strip()

        if len(pattern_text) != 9 or not pattern_text.isdigit():
            return False

        weights = [4, 9, 2, 10, 5, 3]
        total = 0
        for digit_char, weight in zip(pattern_text[:6], weights):
            product = int(digit_char) * weight
            if product > 9:
                product = (product // 10) + (product % 10)
            total += product

        expected_check = total % 10
        return int(pattern_text[6]) == expected_check
