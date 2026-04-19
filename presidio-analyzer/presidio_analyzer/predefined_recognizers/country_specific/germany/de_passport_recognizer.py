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

    Format (9 characters total):
        - 8 alphanumeric characters (uppercase letters from the limited set
          C, F, G, H, J, K, L, M, N, P, R, T, V, W, X, Y, Z and digits 0–9)
          followed by
        - 1 digit at position 9 — the ICAO Doc 9303 check digit over the
          first 8 characters.
        - Example: C01X00T41 (F20400481 verifies against ICAO)

    Character set excludes visually ambiguous letters (A, B, D, E, I, O, Q,
    S, U) per ICAO Doc 9303 Machine Readable Travel Documents.

    Check digit algorithm (ICAO Doc 9303):
        - Letters A=10, B=11, …, Z=35; digits keep their face value.
        - Apply weights 7, 3, 1 repeating to the first 8 characters.
        - Sum the products, take sum mod 10 — that is the 9th digit.

    Worked example for C01X00T41:
        values = 12, 0, 1, 33, 0, 0, 29, 4
        products = 84, 0, 1, 99, 0, 0, 29, 12 → sum = 225 + … (see test)

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

    def validate_result(self, pattern_text: str) -> Optional[bool]:
        """
        Validate the ICAO Doc 9303 check digit at position 9.

        Algorithm source: ICAO Doc 9303 Part 3 — Machine Readable Travel
        Documents. Weights 7, 3, 1 repeating applied to positions 1–8 with
        letters mapped A=10 … Z=35; the sum modulo 10 must equal the digit
        at position 9.

        :param pattern_text: the text to validate (9 characters)
        :return: True if check digit is valid, False otherwise
        """
        pattern_text = pattern_text.upper().strip()

        if len(pattern_text) != 9 or not pattern_text[-1].isdigit():
            return False

        weights = [7, 3, 1]
        total = 0
        for i, c in enumerate(pattern_text[:-1]):
            if c.isdigit():
                value = int(c)
            elif "A" <= c <= "Z":
                value = ord(c) - ord("A") + 10
            else:
                return False
            total += value * weights[i % 3]

        return (total % 10) == int(pattern_text[-1])
