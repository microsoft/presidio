from analyzer import Pattern
from analyzer import PatternRecognizer

CREDIT_CARD_REGEX = r'\b((4\d{3})|(5[0-5]\d{2})|(6\d{3})|(1\d{3})|(3\d{3}))[- ]?(\d{3,4})[- ]?(\d{3,4})[- ]?(\d{3,5})\b'
CREDIT_CARD_CONTEXT = [
    "credit",
    "card",
    "visa",
    "mastercard",
    "cc ",
    # "american express" #TODO: add after adding keyphrase support
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
        patterns = [Pattern('All Credit Cards (weak)', 0.3, CREDIT_CARD_REGEX)]
        context = CREDIT_CARD_CONTEXT
        super().__init__(supported_entities=["CREDIT_CARD"], patterns=patterns, context=context)

    def validate_result(self, text, pattern_result):
        self.__sanitize_value(text)
        res = self.__luhn_checksum()
        if res == 0:
            pattern_result.score = 1

        return pattern_result

    def __luhn_checksum(self):
        def digits_of(n):
            return [int(d) for d in str(n)]

        digits = digits_of(self.sanitized_value)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = 0
        checksum += sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10

    def __sanitize_value(self, text):
        self.sanitized_value = text.replace('-', '').replace(' ', '')
