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
        "DE" + 9 digits

    Examples (fictitious): DE123456789, DE987654321

    Accuracy note: The fixed ``DE`` prefix makes this pattern very specific
    with a very low false-positive rate.  Formal legal validity is confirmed
    via the BZSt/EU VAT verification service, not by local format checks.
    No formal accuracy evaluation has been performed on a labelled dataset.

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
