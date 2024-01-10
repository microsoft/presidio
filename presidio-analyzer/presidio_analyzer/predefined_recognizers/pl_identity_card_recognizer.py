from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class PlIdentityCardRecognizer(PatternRecognizer):
    """
    Recognize Polish identity card number using regex and checksum.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Identity Card",
            r"[A-Z]{3}[0-9]{6}",
            0.1,
        ),
    ]

    CONTEXT = ["numer dowodu"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "pl",
        supported_entity: str = "PL_IDENTITY_CARD",
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
        pattern_text = pattern_text.replace(" ", "")

        letter_offset = 55
        weights_letters = [7, 3, 1]
        weights_digits = [7, 3, 1, 7, 3]

        group_letters = [ord(a) - letter_offset for a in pattern_text[:3]]
        group_digits = [int(a) for a in pattern_text[4:]]

        checksum = sum(
            value * weight for value, weight in zip(group_letters, weights_letters)
        )
        checksum += sum(
            value * weight for value, weight in zip(group_digits, weights_digits)
        )

        return checksum % 10 == int(pattern_text[3])
