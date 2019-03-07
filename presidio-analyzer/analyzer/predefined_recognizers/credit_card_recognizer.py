from analyzer import Pattern
from analyzer import PatternRecognizer
from analyzer.entity_recognizer import EntityRecognizer

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

    def validate_result(self, text, pattern_result):
        self.__sanitize_value(text)
        res = self.__luhn_checksum()
        if res == 0:
            pattern_result.score = EntityRecognizer.MAX_SCORE
        else:
            pattern_result.score = EntityRecognizer.MIN_SCORE

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
