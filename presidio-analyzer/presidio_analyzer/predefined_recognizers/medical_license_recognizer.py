from typing import List, Tuple, Optional

from presidio_analyzer import Pattern, PatternRecognizer

# https://www.meditec.com/blog/dea-numbers-what-do-they-mean


class MedicalLicenseRecognizer(PatternRecognizer):
    """
    Recognize common Medical license numbers using regex + checksum.

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
            "USA DEA Certificate Number (weak)",
            r"[a-zA-Z]{2}\d{7}|[a-zA-Z]{1}9\d{7}",
            0.3,
        ),
    ]

    CONTEXT = [
        "medical",
        "certificate",
        "DEA"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "MEDICAL_LICENSE",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
    ):

        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [("-", ""), (" ", "")]
        )
        context = context if context else self.CONTEXT
        patterns = patterns if patterns else self.PATTERNS
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text: str) -> bool:  # noqa D102
        sanitized_value = self.__sanitize_value(pattern_text, self.replacement_pairs)
        checksum = self.__luhn_checksum(sanitized_value)

        return checksum

    @staticmethod
    def __luhn_checksum(sanitized_value: str) -> bool:
        def digits_of(n: str) -> List[int]:
            return [int(dig) for dig in str(n)]

        digits = digits_of(sanitized_value[2:])
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(str(d * 2)))
        return checksum % 10 == 0

    @staticmethod
    def __sanitize_value(text: str, replacement_pairs: List[Tuple[str, str]]) -> str:
        for search_string, replacement_string in replacement_pairs:
            text = text.replace(search_string, replacement_string)
        return text
