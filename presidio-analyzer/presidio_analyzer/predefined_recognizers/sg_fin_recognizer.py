from presidio_analyzer import Pattern, PatternRecognizer

# Weak pattern: all FIN number start with "S", "T", "F" or "G"
# and ends with a character, e.g., G3311100L
# Ref: https://en.wikipedia.org/wiki/National_Registration_Identity_Card


class SgFinRecognizer(PatternRecognizer):
    """
    Recognizes SG FIN/NRIC number using regex
    """

    PATTERNS = [
        Pattern("Nric (weak)", r"(?i)(\b[A-Z][0-9]{7}[A-Z]\b)", 0.3),
        Pattern("Nric (medium)", r"(?i)(\b[STFG][0-9]{7}[A-Z]\b)", 0.5),
    ]

    CONTEXT = ["fin", "fin#", "nric", "nric#"]

    def __init__(
        self,
        patterns=None,
        context=None,
        supported_language="en",
        supported_entity="SG_NRIC_FIN",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
