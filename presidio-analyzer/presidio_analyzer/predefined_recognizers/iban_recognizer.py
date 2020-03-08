import string

from presidio_analyzer.predefined_recognizers.iban_patterns \
    import regex_per_country
from presidio_analyzer import Pattern, PatternRecognizer

# Import 're2' regex engine if installed, if not- import 'regex'
try:
    import re2 as re
except ImportError:
    import regex as re

IBAN_GENERIC_REGEX = r'\b[A-Z]{2}[0-9]{2}[ ]?([a-zA-Z0-9][ ]?){11,28}\b'
IBAN_GENERIC_SCORE = 0.5

CONTEXT = ["iban", "bank", "transaction"]
LETTERS = {
    ord(d): str(i)
    for i, d in enumerate(string.digits + string.ascii_uppercase)
}


class IbanRecognizer(PatternRecognizer):
    """
    Recognizes IBAN code using regex and checksum
    """

    def __init__(self):
        patterns = [Pattern('IBAN Generic',
                            IBAN_GENERIC_REGEX,
                            IBAN_GENERIC_SCORE)]
        super().__init__(supported_entity="IBAN_CODE",
                         patterns=patterns,
                         context=CONTEXT)

    def validate_result(self, pattern_text):
        pattern_text = pattern_text.replace(' ', '')
        is_valid_checksum = (IbanRecognizer.__generate_iban_check_digits(
            pattern_text) == pattern_text[2:4])
        # score = EntityRecognizer.MIN_SCORE
        result = False
        if is_valid_checksum:
            if IbanRecognizer.__is_valid_format(pattern_text):
                result = True
            elif IbanRecognizer.__is_valid_format(pattern_text.upper()):
                result = None
        return result

    @staticmethod
    def __number_iban(iban):
        return (iban[4:] + iban[:4]).translate(LETTERS)

    @staticmethod
    def __generate_iban_check_digits(iban):
        transformed_iban = (iban[:2] + '00' + iban[4:]).upper()
        number_iban = IbanRecognizer.__number_iban(transformed_iban)
        return '{:0>2}'.format(98 - (int(number_iban) % 97))

    @staticmethod
    def __is_valid_format(iban):
        country_code = iban[:2]
        if country_code in regex_per_country:
            country_regex = regex_per_country[country_code]
            return country_regex and re.match(country_regex, iban,
                                              flags=re.DOTALL | re.MULTILINE)

        return False
