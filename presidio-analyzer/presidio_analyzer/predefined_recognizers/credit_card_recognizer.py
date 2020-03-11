from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer

# pylint: disable=line-too-long
REGEX = r'\b((4\d{3})|(5[0-5]\d{2})|(6\d{3})|(1\d{3})|(3\d{3}))[- ]?(\d{3,4})[- ]?(\d{3,4})[- ]?(\d{3,5})\b'  # noqa: E501
CONTEXT = [
    "credit",
    "card",
    "visa",
    "mastercard",
    "cc ",
    # "american express" #Task #603: Support keyphrases
    "amex",
    "discover",
    "jcb",
    "diners",
    "maestro",
    "instapayment"
]


class CreditCardRecognizer(PatternRecognizer):
    """
    Recognizes common credit card numbers using regex + checksum
    """

    def __init__(self):
        patterns = [Pattern('All Credit Cards (weak)', REGEX, 0.3)]
        super().__init__(supported_entity="CREDIT_CARD", patterns=patterns,
                         context=CONTEXT)

    def validate_result(self, pattern_text):
        sanitized_value = CreditCardRecognizer.__sanitize_value(pattern_text)
        checksum = CreditCardRecognizer.__luhn_checksum(sanitized_value)

        return checksum == 0

    @staticmethod
    def __luhn_checksum(sanitized_value):
        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(sanitized_value)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = 0
        checksum += sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10

    @staticmethod
    def __sanitize_value(text):
        return text.replace('-', '').replace(' ', '')
