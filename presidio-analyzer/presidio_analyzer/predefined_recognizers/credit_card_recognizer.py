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
        checksum = self.__luhn_checksum(sanitized_value)

        return checksum == 0

    def __luhn_checksum(self, sanitized_value):
        def digits_of(n):
            return [int(d) for d in str(n)]

        try:
            digits = digits_of(sanitized_value)
        except ValueError:
            self.logger.exception(f'int conversion failed for sanitized_value: {sanitized_value}')
            return False
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = 0
        checksum += sum(odd_digits)
        for d in even_digits:
            try:
                checksum += sum(digits_of(d * 2))
            except ValueError:
                self.logger.exception(f'int conversion failed for sanitized_value: {sanitized_value} digits: {digits} even_digits: {even_digits}')
                return False
        return checksum % 10

    @staticmethod
    def __sanitize_value(text):
        return text.replace('-', '').replace(' ', '')
