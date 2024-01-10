from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class LtNationalIdNumberRecognizer(PatternRecognizer):
    """
    Recognize national identification number using regex and checksum.

    For more information:
    https://en.wikipedia.org/wiki/National_identification_number#Lithuania

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Asmens Kodas",
            r"[1-6][0-9]{2}(0[1-9]|1[012])([0][1-9]|[1-2][0-9]|3[0-1])[0-9]{4}",
            0.3,
        ),
    ]

    CONTEXT = ["asmens kodas"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "lt",
        supported_entity: str = "LT_ASMENS_KODAS",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str) -> bool:  # noqa D102
        digits = [int(digit) for digit in pattern_text]
        weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 1]
        weights_2 = [3, 4, 5, 6, 7, 8, 9, 1, 2, 3]

        checksum = (
            sum(digit * weight for digit, weight in zip(digits[:10], weights)) % 11
        )

        if checksum < 10:
            return checksum == digits[10]

        checksum = (
            sum(digit * weight for digit, weight in zip(digits[:10], weights_2)) % 11
        )
        if checksum == 10:
            checksum = 0

        return checksum == digits[10]
