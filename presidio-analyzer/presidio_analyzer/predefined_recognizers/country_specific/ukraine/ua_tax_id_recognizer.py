"""Ukrainian individual taxpayer number (РНОКПП) recognizer."""

from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class UaTaxIdRecognizer(PatternRecognizer):
    """
    Recognizes Ukrainian РНОКПП (Реєстраційний номер облікової картки платника податків).

    Also known as ІПН (Ідентифікаційний номер платника податків).
    Always 10 digits with a check digit at position 10 (index 9).

    Checksum algorithm (Державна податкова служба України):
        coefficients = [-1, 5, 7, 9, 4, 6, 10, 5, 7]
        weighted_sum = sum(coefficients[i] * digit[i] for i in range(9))
        check = weighted_sum % 11
        if check >= 10: check = check % 10
        valid if check == digit[9]

    Source: Наказ ДПС України № 822 (2011), офіційний сайт ДПС.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "UA Tax ID / РНОКПП (medium)",
            r"\b\d{10}\b",
            0.3,
        ),
    ]

    CONTEXT = [
        "рнокпп",
        "іпн",
        "ідентифікаційний номер",
        "податковий номер",
        "платник податків",
        "tax id",
        "tin",
    ]

    _COEFFICIENTS = [-1, 5, 7, 9, 4, 6, 10, 5, 7]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "uk",
        supported_entity: str = "UA_TAX_ID",
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
        """Validate РНОКПП check digit."""
        digits = pattern_text.strip()
        if len(digits) != 10 or not digits.isdigit():
            return False
        d = [int(c) for c in digits]
        weighted = sum(self._COEFFICIENTS[i] * d[i] for i in range(9))
        check = weighted % 11
        if check >= 10:
            check = check % 10
        return check == d[9]
