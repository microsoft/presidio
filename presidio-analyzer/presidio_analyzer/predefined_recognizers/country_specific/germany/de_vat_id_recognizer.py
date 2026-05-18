import re
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

    Format (11 characters after normalisation):
        "DE" + 9 digits, where the 9th digit is conventionally a check digit.

    Real-world formatting on invoices and Impressum pages varies:
      DE123456789, DE 123456789, DE-123-456-789, DE 123 456 789, de123456789,
      DE.123.456.789.  The recognizer matches all of these via a lenient
      pattern and normalises them (uppercase, strip whitespace/dashes/dots)
      before applying the structural check.

    Check-digit policy (IMPORTANT — heuristic, not normative):
        The BZSt does NOT publish the USt-IdNr. Prüfziffer algorithm in any
        Merkblatt or normative document. The ISO 7064 Mod 11,10 implemented
        here is the de-facto community consensus (``python-stdnum``, VIES-
        adjacent validators) and matches every officially-publicised test
        vector the authors are aware of. It is empirically reliable for the
        modern digit ranges used by BZSt but has no normative status.

        Rejection policy therefore deliberately errs on the side of keeping
        matches rather than dropping them:

          - Structural failure  (wrong prefix, wrong length after
            normalisation, non-digit body)  → return False (match dropped).
            This is safe — no spec ambiguity.
          - Checksum PASS        → return True (max_score, high confidence).
          - Checksum FAIL        → depends on ``strict_checksum`` parameter:
              * default  (strict_checksum=False): return None. Match keeps
                its base pattern score. A real USt-IdNr that happens to
                fail the heuristic is NEVER silently dropped.
              * strict  (strict_checksum=True):  return False (match
                dropped). Use when false-positive reduction matters more
                than false-negative prevention.

        The default is the enterprise-safe choice: preserves recall on an
        identifier whose authoritative validation path is BZSt/VIES, not
        a locally-implemented checksum.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param strict_checksum: When True, treat the ISO 7064 Mod 11,10 check
        as authoritative and drop matches that fail it. Default False
        (heuristic mode — see policy above).
    :param name: Optional recognizer instance name
    """

    COUNTRY_CODE = "de"

    # Matches in order: continuous form (high confidence), grouped /
    # separator form (slightly lower because separators are rarer). Both
    # are routed through the same validate_result() which normalises first.
    PATTERNS = [
        Pattern(
            "Umsatzsteuer-Identifikationsnummer USt-IdNr. (DE + 9 digits)",
            r"\bDE\d{9}\b",
            0.5,
        ),
        Pattern(
            "Umsatzsteuer-Identifikationsnummer USt-IdNr. (with separators)",
            r"\bDE[\s.\-]?\d{3}[\s.\-]?\d{3}[\s.\-]?\d{3}\b",
            0.4,
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

    # Characters stripped during normalisation. Covers the common real-world
    # formatting variants: "DE 123 456 789", "DE-123-456-789",
    # "DE.123.456.789", and any mixture thereof.
    _NORMALIZATION_STRIP = re.compile(r"[\s.\-]")

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_VAT_ID",
        strict_checksum: bool = False,
        name: Optional[str] = None,
    ):
        self.strict_checksum = strict_checksum
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
        Validate the USt-IdNr. after real-world-tolerant normalisation.

        Returns are tri-state to reflect spec uncertainty (see class
        docstring):

          True   — structural check + ISO 7064 Mod 11,10 checksum pass.
          False  — structural check failed, OR checksum failed in strict
                   mode.
          None   — structural check passed but checksum failed in the
                   default (non-strict) mode: the match keeps its pattern
                   score rather than being silently dropped.

        :param pattern_text: the raw matched text (possibly with spaces,
            dashes, dots and mixed case).
        :return: True / False / None per the semantics above.
        """
        # Normalise: uppercase, drop separators. Covers real-world formatting
        # such as "DE 123 456 789", "de-123-456-789", "DE.123.456.789".
        normalized = self._NORMALIZATION_STRIP.sub("", pattern_text.upper())

        # Structural checks — unambiguous, safe to reject outright.
        if len(normalized) != 11 or not normalized.startswith("DE"):
            return False

        digits = normalized[2:]
        if not digits.isdigit():
            return False

        # Heuristic check digit (ISO 7064 Mod 11,10). Not published by BZSt.
        # See class docstring for the rejection policy rationale.
        product = 10
        for i in range(8):
            total = (int(digits[i]) + product) % 10
            if total == 0:
                total = 10
            product = (total * 2) % 11

        check = 11 - product
        if check == 10:
            check = 0

        if check == int(digits[8]):
            return True

        # Checksum mismatch: strict mode rejects, default mode abstains.
        # Default mode (None) preserves recall against the real-world risk
        # that BZSt uses a wider algorithm than the community consensus.
        return False if self.strict_checksum else None
