from presidio_analyzer import Pattern, PatternRecognizer

# Weak pattern: all FIN number start with "S", "T", "F" or "G"
# and ends with a character, e.g., G3311100L
# Ref: https://en.wikipedia.org/wiki/National_Registration_Identity_Card


class SgFinRecognizer(PatternRecognizer):
    """
    Recognizes SG FIN/NRIC number using regex
    """

    PATTERN_GROUPS = [
        ("Nric (weak)", r"(?i)(\b[A-Z][0-9]{7}[A-Z]\b)", 0.3),
        ("Nric (medium)", r"(?i)(\b[STFG][0-9]{7}[A-Z]\b)", 0.5),
    ]

    CONTEXT = ["fin", "fin#", "nric", "nric#"]

    def __init__(
        self,
        pattern_groups=None,
        context=None,
        supported_language="en",
        supported_entity="US_SSN",
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
