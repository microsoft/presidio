from presidio_analyzer import Pattern, PatternRecognizer


class UsBankRecognizer(PatternRecognizer):
    """
    Recognizes US bank number using regex
    """

    PATTERN_GROUPS = [
        ("Bank Account (weak)", r"\b[0-9]{8,17}\b", 0.05,),
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
        pattern_groups=None,
        context=None,
        supported_language="en",
        supported_entity="US_BANK_NUMBER",
    ):
        pattern_groups = pattern_groups if pattern_groups else self.PATTERN_GROUPS
        context = context if context else self.CONTEXT
        patterns = [Pattern(*pattern_group) for pattern_group in pattern_groups]
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
