from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class InVoterRecognizer(PatternRecognizer):
    """
    Recognize Indian Voter/Election Id(EPIC).

    The Elector's Photo Identity Card or Voter id is a ten digit
    alpha-numeric code issued by Election Commission of India
    to adult domiciles who have reached the age of 18
    Ref: https://en.wikipedia.org/wiki/Voter_ID_(India)

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "VOTER",
            r"\b([A-Za-z]{1}[ABCDGHJKMNPRSYabcdghjkmnprsy]{1}[A-Za-z]{1}([0-9]){7})\b",
            0.4,
        ),
        Pattern(
            "VOTER",
            r"\b([A-Za-z]){3}([0-9]){7}\b",
            0.3,
        ),
    ]

    CONTEXT = [
        "voter",
        "epic",
        "elector photo identity card",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "IN_VOTER",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            supported_entity=supported_entity,
        )
