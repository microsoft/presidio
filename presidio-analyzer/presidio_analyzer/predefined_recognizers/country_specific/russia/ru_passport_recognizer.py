"""Russian internal passport number recognizer."""

from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class RuPassportRecognizer(PatternRecognizer):
    """
    Recognizes Russian internal passport (Паспорт гражданина РФ) numbers.

    Format: 4-digit series + 6-digit number.
    - First 2 digits of series: region code (01–99).
    - Second 2 digits of series: year of issue (last two digits).
    - Series and number are separated by a space or written together.
    Examples: «45 10 123456», «4510 123456», «4510123456».

    No check digit is defined for this document.

    Source: Постановление Правительства РФ № 828 (1997, с изм.),
    Приказ МВД России № 851 (2017).

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        # Series with space between region/year and between series/number: "45 10 123456"
        Pattern(
            "RU Passport with spaces (medium)",
            r"\b\d{2}\s\d{2}\s\d{6}\b",
            0.5,
        ),
        # Series and number separated by one space: "4510 123456"
        Pattern(
            "RU Passport series+number (medium)",
            r"\b\d{4}\s\d{6}\b",
            0.4,
        ),
        # No separators: "4510123456"
        Pattern(
            "RU Passport no separator (weak)",
            r"\b\d{10}\b",
            0.05,
        ),
    ]

    CONTEXT = [
        "паспорт",
        "серия",
        "номер паспорта",
        "паспорт гражданина",
        "российский паспорт",
        "документ",
        "удостоверение личности",
        "passport",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "ru",
        supported_entity: str = "RU_PASSPORT",
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
