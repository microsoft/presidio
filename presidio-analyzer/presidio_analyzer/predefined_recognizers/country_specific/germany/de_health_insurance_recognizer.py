import re
from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DeHealthInsuranceRecognizer(PatternRecognizer):
    """
    Recognizes German statutory health insurance numbers (KVNR).

    Also called Krankenversicherungsnummer, Krankenversichertennummer, or
    Versichertennummer.

    The KVNR is assigned to every person insured under the German statutory
    health insurance system (gesetzliche Krankenversicherung, GKV). It is printed on the
    Gesundheitskarte (eGK – elektronische Gesundheitskarte).

    Legal basis: § 290 SGB V (Sozialgesetzbuch Fünftes Buch – Gesetzliche
    Krankenversicherung).
    Data protection: DSGVO Art. 9 (besondere Kategorien personenbezogener Daten –
    Gesundheitsdaten), BDSG § 22.

    Format (10 characters):
        Pos 1:    Buchstabe (first letter of birth surname, A–Z)
        Pos 2–9:  8 digits (birth date encoded + serial)
        Pos 10:   Prüfziffer (check digit, 0–9)

    Example: A000500015 (from § 290 SGB V Anlage 1, Stand 02.01.2023)

    Check digit algorithm (§ 290 SGB V Anlage 1, GKV-Spitzenverband):
        1. Convert the letter at position 1 to its 2-digit ordinal value
           (A=01, B=02, …, Z=26). Concatenated with the 8 data digits at
           positions 2–9, this yields 10 effective digits.
        2. Apply alternating factors [1, 2, 1, 2, 1, 2, 1, 2, 1, 2] to those
           10 effective digits.
        3. For each product ≥ 10, replace it with the cross-sum of its digits
           (Quersumme).
        4. Sum the 10 values; compute sum mod 10.
        5. The result must equal the check digit at position 10.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    COUNTRY_CODE = "de"

    # Accuracy note: The base pattern `[A-Z]\d{9}` is intentionally broad (any
    # uppercase letter followed by 9 digits) because no more specific structural
    # constraint exists in the KVNR format beyond length and the leading letter.
    # The GKV checksum validation in validate_result() is the primary defence
    # against false positives; the base confidence is therefore kept low (0.3)
    # and context words are required for high-confidence matches.
    # Formal accuracy evaluation has not been performed on a labelled dataset.
    PATTERNS = [
        Pattern(
            "Krankenversicherungsnummer KVNR (letter + 9 digits)",
            r"\b[A-Z]\d{9}\b",
            0.3,
        ),
    ]

    CONTEXT = [
        "krankenversicherungsnummer",
        "krankenversichertennummer",
        "versichertennummer",
        "kvnr",
        "krankenkasse",
        "krankenversicherung",
        "gesundheitskarte",
        "egk",
        "elektronische gesundheitskarte",
        "gkv",
        "gesetzliche krankenversicherung",
        "krankenversicherungsausweis",
        "versichertenausweis",
        "versichertenkarte",
        "aok",
        "tkk",
        "barmer",
        "dak",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_HEALTH_INSURANCE",
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
        Validate the KVNR using the GKV-Spitzenverband checksum algorithm.

        Algorithm source: GKV-Spitzenverband technical specification (§ 290 SGB V).

        :param pattern_text: the text to validate (10 characters: 1 letter + 9 digits)
        :return: True if valid, False if invalid
        """
        pattern_text = pattern_text.upper().strip()

        if len(pattern_text) != 10:
            return False

        if not re.match(r"^[A-Z]\d{9}$", pattern_text):
            return False

        letter = pattern_text[0]
        letter_val = str(ord(letter) - ord("A") + 1).zfill(2)

        # Letter expanded to 2 digits + 8 data digits = 10 effective digits
        effective = letter_val + pattern_text[1:9]

        check_digit = int(pattern_text[9])
        factors = [1, 2, 1, 2, 1, 2, 1, 2, 1, 2]

        total = 0
        for digit_char, factor in zip(effective, factors):
            product = int(digit_char) * factor
            if product >= 10:
                product = (product // 10) + (product % 10)
            total += product

        return (total % 10) == check_digit
