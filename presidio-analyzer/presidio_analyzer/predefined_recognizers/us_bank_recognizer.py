from typing import Optional, List

from presidio_analyzer import Pattern, PatternRecognizer


class UsBankRecognizer(PatternRecognizer):
    """
    Recognizes US bank number using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Bank Account (weak)",
            r"\b[0-9]{8,17}\b",
            0.05,
        ),
    ]

    CONTEXT = [
        "bank"
        # Task #603: Support keyphrases: change to "checking account"
        # as part of keyphrase change
        "check",
        "account",
        "account#",
        "acct",
        "save",
        "debit",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "US_BANK_NUMBER",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
