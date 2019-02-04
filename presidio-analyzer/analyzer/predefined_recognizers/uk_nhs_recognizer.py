from analyzer import Pattern
from analyzer import PatternRecognizer

NHS_REGEX = r'\b([0-9]{3})[- ]?([0-9]{3})[- ]?([0-9]{4})\b'
NHS_CONTEXT = [
    "national health service", "nhs", "health services authority",
    "health authority"
]


class NhsRecognizer(PatternRecognizer):
    """
    Recognizes NHS number using regex and checksum
    """

    def __init__(self):
        patterns = [Pattern('NHS (medium)', 0.5, NHS_REGEX)]
        super().__init__(supported_entities=["UK_NHS"], patterns=patterns, context=NHS_CONTEXT)

    def validate_pattern_logic(self, text, pattern_result):
        text = NhsRecognizer.__sanitize_value(text)

        multiplier = 10
        total = 0
        for c in text:
            val = int(c)
            total = total + val * multiplier
            multiplier = multiplier - 1

        remainder = total % 11
        check_digit = 11 - remainder

        pattern_result.score = 1.0 if check_digit is 11 else 0
        return pattern_result

    @staticmethod
    def __sanitize_value(text):
        return text.replace('-', '').replace(' ', '')
