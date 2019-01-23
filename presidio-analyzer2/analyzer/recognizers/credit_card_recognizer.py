from pattern_recognizer import PatternRecognizer
from pattern import Pattern

class CreditCardRecognizer(PatternRecognizer):

    def get_supported_fields(self):
        return "CREDIT_CARD"
    
    def get_patterns(self):
        patterns = []
        r = r'\b((4\d{3})|(5[0-5]\d{2})|(6\d{3})|(1\d{3})|(3\d{3}))[- ]?(\d{3,4})[- ]?(\d{3,4})[- ]?(\d{3,5})\b'  # noqa: E501
        p = Pattern('All Credit Cards (weak)', 0.3, r)
        patterns.append(p)

        return patterns
    
    def validate_pattern(self, text):
        self.__sanitize_value(text)
        return self.__luhn_checksum() == 0

    def get_context(self):
        return [
        "credit",
        "card",
        "visa",
        "mastercard",
        # "american express" #TODO: add after adding keyphrase support
        "amex",
        "discover",
        "jcb",
        "diners",
        "maestro",
        "instapayment"
    ]

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


