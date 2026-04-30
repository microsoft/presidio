"""Ukrainian passport number recognizer."""

from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class UaPassportRecognizer(PatternRecognizer):
    """
    Recognizes Ukrainian passport numbers.

    Two formats are in use:
    - Old internal passport (до 2015): two-letter Cyrillic series + 6 digits,
      e.g. «АА 123456» or «КВ123456».
      Source: Закон України «Про Єдиний державний демографічний реєстр» (2012).
    - New biometric passport / ID-card (з 2015): 9-digit book number printed on
      the cover, and a two-letter Latin + 6-digit machine-readable series on the
      data page, e.g. «AA 123456».
      Source: Постанова КМУ № 302 (2015).

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        # Old-format: Cyrillic 2-letter series + optional space + 6 digits
        Pattern(
            "UA Passport old format (medium)",
            r"\b[А-ЯІЇЄҐ]{2}\s?\d{6}\b",
            0.5,
        ),
        # Biometric MRZ series: 2 Latin uppercase + optional space + 6 digits
        Pattern(
            "UA Passport biometric MRZ (medium)",
            r"\b[A-Z]{2}\s?\d{6}\b",
            0.4,
        ),
        # Biometric book number: 9 consecutive digits
        Pattern(
            "UA Passport biometric book number (weak)",
            r"\b\d{9}\b",
            0.05,
        ),
    ]

    CONTEXT = [
        "паспорт",
        "закордонний паспорт",
        "серія",
        "номер паспорта",
        "passport",
        "документ",
        "посвідчення особи",
        "id-картка",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "uk",
        supported_entity: str = "UA_PASSPORT",
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
