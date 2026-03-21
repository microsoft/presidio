import re
from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DeSocialSecurityRecognizer(PatternRecognizer):
    """
    Recognizes German Rentenversicherungsnummer (RVNR / Sozialversicherungsnummer).

    The Rentenversicherungsnummer (also called Versicherungsnummer or RVNR) is a
    unique 12-character identifier assigned to every person insured under the German
    statutory pension insurance scheme (gesetzliche Rentenversicherung). It encodes
    date of birth, gender information, and a serial number.

    Legal basis: § 147 SGB VI (Sozialgesetzbuch Sechstes Buch – Gesetzliche
    Rentenversicherung), § 33a SGB I.
    Data protection: DSGVO Art. 4 Nr. 1 (personenbezogene Daten), BDSG.

    Format (12 characters):
        Pos 1–2:   Bereichsnummer (2 digits, issuing regional office code, 01–99)
        Pos 3–4:   Geburtstag (birth day, 01–31; or 51–81 for women with
                   Ergänzungsmerkmal)
        Pos 5–6:   Geburtsmonat (birth month, 01–12)
        Pos 7–8:   Geburtsjahr (last 2 digits of birth year)
        Pos 9:     Buchstabenkennung (first letter of birth surname, A–Z)
        Pos 10–11: Seriennummer (2-digit ordinal, 01–49 male / 50–99 female as
                   Ergänzungsmerkmal)
        Pos 12:    Prüfziffer (check digit)

    Example (fictitious): 65070803A012

    Check digit algorithm (Deutsche Rentenversicherung):
        1. Replace the letter at position 9 with its 2-digit ordinal value
           (A=01, B=02, …, Z=26), yielding an effective 13-digit string.
        2. Apply weights [2,1,2,1,2,1,2,1,2,1,2,1] to the first 12 effective digits.
        3. For each product ≥ 10, replace it with the sum of its digits.
        4. Sum all 12 values, compute sum mod 10.
        5. The result must equal the check digit at position 12 (pos 13 in effective).

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Rentenversicherungsnummer (Strict, with birth date structure)",
            r"\b\d{2}"
            r"(0[1-9]|[12]\d|3[01]|5[1-9]|[67]\d|8[01])"  # day: 01-31 or 51-81
            r"(0[1-9]|1[0-2])"                              # month 01-12
            r"\d{2}"                                  # year
            r"[A-Z]"                                  # surname initial
            r"\d{2}"                                  # serial
            r"[0-9]\b",                               # check digit
            0.5,
        ),
        Pattern(
            "Rentenversicherungsnummer (Relaxed)",
            r"\b\d{8}[A-Z]\d{3}\b",
            0.3,
        ),
    ]

    CONTEXT = [
        "rentenversicherungsnummer",
        "sozialversicherungsnummer",
        "versicherungsnummer",
        "rvnr",
        "svnr",
        "sv-nummer",
        "rente",
        "rentenversicherung",
        "deutsche rentenversicherung",
        "drv",
        "sozialversicherung",
        "sozialversicherungsausweis",
        "rentenausweis",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_SOCIAL_SECURITY",
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
        Validate the Rentenversicherungsnummer using the official checksum.

        Algorithm source: Deutsche Rentenversicherung Bund, technical specification
        for RVNR validation.

        :param pattern_text: the text to validate (12 characters)
        :return: True if valid, False if invalid
        """
        pattern_text = pattern_text.upper().strip()

        if len(pattern_text) != 12:
            return False

        if not re.match(r"^\d{8}[A-Z]\d{3}$", pattern_text):
            return False

        letter = pattern_text[8]
        letter_val = str(ord(letter) - ord("A") + 1).zfill(2)

        # Effective 12-digit string:
        # positions 1-8 + letter as 2 digits + positions 10-11
        effective = pattern_text[:8] + letter_val + pattern_text[9:11]

        check_digit = int(pattern_text[11])
        weights = [2, 1, 2, 1, 2, 1, 2, 1, 2, 1, 2, 1]

        total = 0
        for digit_char, weight in zip(effective, weights):
            product = int(digit_char) * weight
            if product >= 10:
                product = (product // 10) + (product % 10)
            total += product

        return (total % 10) == check_digit
