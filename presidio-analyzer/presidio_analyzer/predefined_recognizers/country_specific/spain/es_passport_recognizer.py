from typing import List, Optional

import regex as re

from presidio_analyzer import Pattern, PatternRecognizer


class EsPassportRecognizer(PatternRecognizer):
    """
    Recognize Spanish passport numbers using regex.

    Follows the format: 3 letters followed by 6 digits (e.g. AAA123456).

    Reference(s):
    https://en.wikipedia.org/wiki/Spanish_passport

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    COUNTRY_CODE = "es"

    PATTERNS = [
        Pattern(
            "ES_PASSPORT",
            r"\b[A-Z]{3}[0-9]{6}\b",
            0.05,
        ),
    ]

    CONTEXT = ["pasaporte", "passport", "número de pasaporte", "passport number"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "es",
        supported_entity: str = "ES_PASSPORT",
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
            global_regex_flags=re.DOTALL | re.MULTILINE | re.IGNORECASE,
        )
