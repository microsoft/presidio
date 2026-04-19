from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DeVatIdRecognizer(PatternRecognizer):
    """
    Recognizes German Umsatzsteuer-Identifikationsnummer (USt-IdNr.).

    The USt-IdNr. is issued by the Bundeszentralamt für Steuern (BZSt) to
    VAT-registered businesses and self-employed persons in Germany.  It is
    used on invoices and cross-border EU transactions.  While primarily a
    business identifier, it can identify sole traders and freelancers (natural
    persons) and may therefore constitute personal data under DSGVO Art. 4
    Nr. 1 when linked to an individual.

    Legal basis: § 27a UStG (Umsatzsteuergesetz).
    Format documentation: BZSt (Bundeszentralamt für Steuern).
    Data protection: DSGVO Art. 4 Nr. 1 (if linked to a natural person), BDSG.

    Format (11 characters):
        "DE" + 9 digits, where the 9th digit is a check digit.

    Examples: DE136695976, DE129273398 (both verify against the checksum)

    Check digit algorithm (ISO 7064 Mod 11,10):
        The BZSt does not publish the Prüfziffer algorithm in an official
        Merkblatt, but the algorithm used for the USt-IdNr. is identical to
        the one for the Steuer-IdNr. (ISO 7064 Mod 11,10). It is widely
        adopted in community implementations such as ``python-stdnum`` and
        VIES-adjacent validators. Returning True here means only that the
        structural check digit is consistent — formal legal validity must
        still be confirmed via BZSt/VIES.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Umsatzsteuer-Identifikationsnummer USt-IdNr. (DE + 9 digits)",
            r"\bDE\d{9}\b",
            0.5,
        ),
    ]

    CONTEXT = [
        "umsatzsteuer-identifikationsnummer",
        "umsatzsteueridentifikationsnummer",
        "ust-idnr",
        "ust-id",
        "ustidnr",
        "umsatzsteuer-id",
        "mehrwertsteuer",
        "vat",
        "vat-id",
        "vat id",
        "steueridentifikation",
        "bzst",
        "bundeszentralamt für steuern",
        "finanzamt",
        "invoice",
        "rechnung",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_VAT_ID",
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
        Validate the USt-IdNr. structural check digit (ISO 7064 Mod 11,10).

        Not an authoritative existence check — only confirms the 9-digit
        body has a consistent Prüfziffer. For legal validity use BZSt/VIES.

        :param pattern_text: the text to validate ("DE" + 9 digits)
        :return: True if check digit is valid, False otherwise
        """
        pattern_text = pattern_text.upper().strip()

        if len(pattern_text) != 11 or not pattern_text.startswith("DE"):
            return False

        digits = pattern_text[2:]
        if not digits.isdigit():
            return False

        product = 10
        for i in range(8):
            total = (int(digits[i]) + product) % 10
            if total == 0:
                total = 10
            product = (total * 2) % 11

        check = 11 - product
        if check == 10:
            check = 0

        return check == int(digits[8])
