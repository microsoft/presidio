from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DeTaxIdRecognizer(PatternRecognizer):
    """
    Recognizes German Steueridentifikationsnummer (Steuer-IdNr.) using regex and checksum.

    The Steueridentifikationsnummer is a unique 11-digit personal tax identification
    number issued by the Bundeszentralamt für Steuern to every person registered in
    Germany. It does not change over a person's lifetime.

    Legal basis: §§ 139a–139e Abgabenordnung (AO), in force since 2007.
    Data protection: DSGVO Art. 4 Nr. 1 (personenbezogene Daten), BDSG.

    Format:
        - 11 digits
        - First digit: 1–9 (never 0)
        - Digits 2–10: no digit may appear more than 3 times
        - Digit 11: check digit (ISO 7064 Mod 11, 10 variant)

    Examples (fictitious): 02476291358, 86095742719

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Steueridentifikationsnummer (High)",
            r"\b[1-9]\d{10}\b",
            0.5,
        ),
    ]

    CONTEXT = [
        "steueridentifikationsnummer",
        "steuer-id",
        "steuerid",
        "steuerliche identifikationsnummer",
        "steuerliche identifikation",
        "persönliche identifikationsnummer",
        "steuer identifikation",
        "idnr",
        "steuer-idnr",
        "steuernummer",
        "bzst",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_TAX_ID",
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
        Validate the Steueridentifikationsnummer using the official checksum algorithm.

        Algorithm: ISO 7064 Mod 11, 10 variant as specified by the
        Bundeszentralamt für Steuern.

        :param pattern_text: the text to validate (11 digits)
        :return: True if valid, False if invalid
        """
        if len(pattern_text) != 11 or not pattern_text.isdigit():
            return False
        if pattern_text[0] == "0":
            return False

        digits = [int(d) for d in pattern_text]

        # Check that the first 10 digits do not consist of the same digit repeated
        if len(set(digits[:10])) == 1:
            return False

        # ISO 7064 Mod 11, 10 checksum
        product = 10
        for i in range(10):
            total = (digits[i] + product) % 10
            if total == 0:
                total = 10
            product = (total * 2) % 11

        check = 11 - product
        if check == 10:
            check = 0

        return check == digits[10]
