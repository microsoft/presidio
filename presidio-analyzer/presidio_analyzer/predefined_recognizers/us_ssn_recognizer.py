from collections import defaultdict

from presidio_analyzer import Pattern, PatternRecognizer


# pylint: disable=line-too-long,abstract-method
class UsSsnRecognizer(PatternRecognizer):
    """
    Recognizes US Social Security Number (SSN) using regex
    """

    PATTERNS = [
        Pattern("SSN (very weak)", r"\b(([0-9]{5})-([0-9]{4})|([0-9]{3})-([0-9]{6}))\b", 0.05),  # noqa E501
        Pattern("SSN (weak)", r"\b[0-9]{9}\b", 0.3),
        Pattern("SSN (medium)", r"\b([0-9]{3})[- .]([0-9]{2})[- .]([0-9]{4})\b", 0.5),
    ]

    CONTEXT = [
        "social",
        "security",
        # "sec", # Task #603: Support keyphrases ("social sec")
        "ssn",
        "ssns",
        "ssn#",
        "ss#",
        "ssid",
    ]

    def __init__(
        self,
        patterns=None,
        context=None,
        supported_language="en",
        supported_entity="US_SSN",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def invalidate_result(self, pattern_text):
        # if there are delimiters, make sure both delimiters are the same
        delimiter_counts = defaultdict(int)
        for c in pattern_text:
            if c in ('.', '-', ' '):
                delimiter_counts[c] += 1
        if any(count == 1 for count in delimiter_counts.values()):
            # mismatched delimiters
            return True

        only_digits = ''.join(c for c in pattern_text if c.isdigit())
        if all(only_digits[0] == c for c in only_digits):
            # cannot be all same digit
            return True

        if only_digits[3:5] == '00' or only_digits[5:] == '0000':
            # groups cannot be all zeros
            return True

        for sample_ssn in ('000', '666', '123456789', '98765432', '078051120'):
            if only_digits.startswith(sample_ssn):
                return True

        return False
