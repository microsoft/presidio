from typing import Optional, List

from presidio_analyzer import Pattern, PatternRecognizer
from regex import Match


ITIN_REGEX = r"\b9\d{2}(?P<firstSeparator>[- ]?)(5\d|6[0-5]|7\d|8[0-8]|9([0-2]|[4-9]))(?P<secondSeparator>[- ]?)\d{4}\b"  # noqa: E501


def improve_itin_pattern(pattern: Pattern, match: Match) -> Pattern:
    first_separator = match.group('firstSeparator')
    second_separator = match.group('secondSeparator')

    if first_separator and second_separator:
        return pattern

    if not first_separator and not second_separator:
        return Pattern(
            "Itin (weak)",
            pattern.regex,
            0.3
        )

    return Pattern(
        "Itin (very weak)",
        pattern.regex,
        0.05
    )


class UsItinRecognizer(PatternRecognizer):
    """
    Recognizes US ITIN (Individual Taxpayer Identification Number) using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Itin (medium)",
            ITIN_REGEX,
            0.5,
            improve_itin_pattern,
        ),
    ]

    CONTEXT = ["individual", "taxpayer", "itin", "tax", "payer", "taxid", "tin"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "US_ITIN",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

