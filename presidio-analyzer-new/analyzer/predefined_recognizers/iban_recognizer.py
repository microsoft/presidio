from analyzer import Pattern
from analyzer import PatternRecognizer
import string

IBAN_REGEX = u'[a-zA-Z]{2}[0-9]{2}[a-zA-Z0-9]{4}[0-9]{7}([a-zA-Z0-9]?){0,16}'
IBAN_CONTEXT = ["iban"]
LETTERS = {
    ord(d): str(i)
    for i, d in enumerate(string.digits + string.ascii_uppercase)
}


class IbanRecognizer(PatternRecognizer):
    """
    Recognizes IBAN code using regex and checksum
    """

    def __init__(self):
        patterns = [Pattern('Iban (Medium)', 0.5, IBAN_REGEX)]
        super().__init__(supported_entities=["IBAN_CODE"], patterns=patterns, context=IBAN_CONTEXT)

    def validate_pattern_logic(self, text, pattern_result):
        is_valid_iban = IbanRecognizer.__generate_iban_check_digits(
            text) == text[2:4] and IbanRecognizer.__valid_iban(text)

        pattern_result.score = 1.0 if is_valid_iban else 0
        return pattern_result


    @staticmethod
    def __number_iban(iban):
        return (iban[4:] + iban[:4]).translate(LETTERS)

    @staticmethod
    def __generate_iban_check_digits(iban):
        number_iban = IbanRecognizer.__number_iban(iban[:2] + '00' + iban[4:])
        return '{:0>2}'.format(98 - (int(number_iban) % 97))

    @staticmethod
    def __valid_iban(iban):
        return int(IbanRecognizer.__number_iban(iban)) % 97 == 1
