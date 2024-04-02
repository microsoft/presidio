from typing import Optional, List, Tuple

from presidio_analyzer import Pattern, PatternRecognizer

class InPassportRecognizer(PatternRecognizer):
    """
    Indian Passport Recognizer
    """

    PATTERNS = [
        Pattern(
            "PASSPORT",
            r"\b[A-Z][1-9][0-9]{2}[0-9]{4}[1-9]\b",
            0.7,
        ),
    ]

    CONTEXT = [
        "passport",
        "indian passport",
        "passport number"
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "IN_PASSPORT",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )


