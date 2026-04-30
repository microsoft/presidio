"""Ukrainian pension/social-insurance account number recognizer."""

from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class UaPensionIdRecognizer(PatternRecognizer):
    """
    Recognizes Ukrainian pension certificate (personal account) numbers.

    The Пенсійний фонд України assigns each insured person a unique
    13-digit personal account number printed on the pension certificate
    (Свідоцтво про загальнообов'язкове державне соціальне страхування).

    Format: 13 consecutive digits.
    No public checksum algorithm is specified by the ПФУ.

    Source: Закон України «Про збір та облік єдиного внеску на
    загальнообов'язкове державне соціальне страхування» № 2464-VI (2010).

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "UA Pension ID (weak)",
            r"\b\d{13}\b",
            0.1,
        ),
    ]

    CONTEXT = [
        "пенсійний фонд",
        "свідоцтво соціального страхування",
        "особовий рахунок",
        "пфу",
        "соціальне страхування",
        "pension",
        "social insurance",
        "пан",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "uk",
        supported_entity: str = "UA_PENSION_ID",
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
