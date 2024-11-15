from typing import List, Optional, Tuple

from presidio_analyzer import Pattern, PatternRecognizer


class NhsRecognizer(PatternRecognizer):
    """
    Recognizes NHS number using regex and checksum.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    This can allow a greater variety in input, for example by removing dashes or spaces.
    """

    PATTERNS = [
        Pattern(
            "NHS (medium)",
            r"\b([0-9]{3})[- ]?([0-9]{3})[- ]?([0-9]{4})\b",
            0.5,
        ),
    ]

    CONTEXT = [
        "national health service",
        "nhs",
        "health services authority",
        "health authority",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "UK_NHS",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [("-", ""), (" ", "")]
        )
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str) -> bool:
        """
        Validate the pattern logic e.g., by running checksum on a detected pattern.

        :param pattern_text: the text to validated.
        Only the part in text that was detected by the regex engine
        :return: A bool indicating whether the validation was successful.
        """
        text = self.__sanitize_value(pattern_text, self.replacement_pairs)
        total = sum(
            [int(c) * multiplier for c, multiplier in zip(text, reversed(range(11)))]
        )
        remainder = total % 11
        check_remainder = remainder == 0

        return check_remainder

    @staticmethod
    def __sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text
