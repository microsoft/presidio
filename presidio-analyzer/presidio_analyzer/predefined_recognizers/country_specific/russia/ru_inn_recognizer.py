"""Russian Individual Taxpayer Number (ИНН) recognizer."""

from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class RuInnRecognizer(PatternRecognizer):
    """
    Recognizes Russian ИНН (Идентификационный номер налогоплательщика).

    Two variants:
    - 10-digit ИНН for legal entities (организации).
    - 12-digit ИНН for individuals (физические лица).

    Checksum algorithm (ФНС России):

    For 10-digit ИНН:
        weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]
        check = sum(weights[i] * digit[i] for i in 0..8) % 11 % 10
        valid if check == digit[9]

    For 12-digit ИНН:
        w11 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        w12 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        c11 = sum(w11[i] * digit[i] for i in 0..9) % 11 % 10
        c12 = sum(w12[i] * digit[i] for i in 0..10) % 11 % 10
        valid if c11 == digit[10] and c12 == digit[11]

    Source: Приказ ФНС России № ММВ-7-6/435@ (2012),
    https://www.nalog.gov.ru/rn77/taxation/reference_work/inn/.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "RU INN individual 12-digit (medium)",
            r"\b\d{12}\b",
            0.3,
        ),
        Pattern(
            "RU INN organization 10-digit (medium)",
            r"\b\d{10}\b",
            0.3,
        ),
    ]

    CONTEXT = [
        "инн",
        "идентификационный номер налогоплательщика",
        "налоговый номер",
        "налогоплательщик",
        "фнс",
        "tax id",
        "tin",
    ]

    _W10 = [2, 4, 10, 3, 5, 9, 4, 6, 8]
    _W11 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    _W12 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "ru",
        supported_entity: str = "RU_TAX_ID",
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
        """Validate ИНН check digit(s)."""
        digits = pattern_text.strip()
        if not digits.isdigit():
            return False
        d = [int(c) for c in digits]

        if len(d) == 10:
            check = sum(self._W10[i] * d[i] for i in range(9)) % 11 % 10
            return check == d[9]

        if len(d) == 12:
            c11 = sum(self._W11[i] * d[i] for i in range(10)) % 11 % 10
            c12 = sum(self._W12[i] * d[i] for i in range(11)) % 11 % 10
            return c11 == d[10] and c12 == d[11]

        return False
