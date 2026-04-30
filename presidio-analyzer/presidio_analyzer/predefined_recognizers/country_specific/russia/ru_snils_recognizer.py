"""Russian pension insurance number (СНИЛС) recognizer."""

from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class RuSnilsRecognizer(PatternRecognizer):
    """
    Recognizes Russian СНИЛС (Страховой номер индивидуального лицевого счёта).

    Format: 11 digits, typically printed as XXX-XXX-XXX XX.
    The last two digits are a control number computed from the first nine.

    Checksum algorithm (ПФР):
        weighted_sum = sum(digit[i] * (9 - i) for i in range(9))
        control = weighted_sum % 101
        if control in (100, 101): control = 0
        valid if control == int(digits[9:11])

    Note: numbers 001-001-998 through 001-001-999 are reserved test values
    and are not issued; the algorithm yields control=0 for them.

    Source: Постановление Правления ПФ РФ № 318п (2015),
    https://www.pfr.gov.ru/grazhdanam/snils/.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        # Canonical dashed format: "XXX-XXX-XXX XX"
        Pattern(
            "RU SNILS dashed (high)",
            r"\b\d{3}-\d{3}-\d{3}\s\d{2}\b",
            0.7,
        ),
        # No separators: 11 consecutive digits
        Pattern(
            "RU SNILS no separator (weak)",
            r"\b\d{11}\b",
            0.05,
        ),
    ]

    CONTEXT = [
        "снилс",
        "страховой номер",
        "индивидуальный лицевой счёт",
        "пенсионный фонд",
        "пфр",
        "социальное страхование",
        "pension",
        "social insurance",
        "пан",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "ru",
        supported_entity: str = "RU_SNILS",
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
        """Validate СНИЛС control number."""
        digits = "".join(c for c in pattern_text if c.isdigit())
        if len(digits) != 11:
            return False
        d = [int(c) for c in digits]
        weighted = sum(d[i] * (9 - i) for i in range(9))
        control = weighted % 101
        if control >= 100:
            control = 0
        return control == int(digits[9:11])
