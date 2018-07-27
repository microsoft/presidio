import string
from field_types import field_type, field_pattern


class Iban(field_type.FieldType):
    name = "IBAN_CODE"
    context = ["iban"]
    should_check_checksum = True

    patterns = []

    pattern = field_pattern.FieldPattern()
    pattern.regex = u'[a-zA-Z]{2}[0-9]{2}[a-zA-Z0-9]{4}[0-9]{7}([a-zA-Z0-9]?){0,16}'
    pattern.name = 'Iban (Medium)'
    pattern.strength = 0.5
    patterns.append(pattern)

    def check_checksum(self):
        LETTERS = {
            ord(d): str(i)
            for i, d in enumerate(string.digits + string.ascii_uppercase)
        }

        def __number_iban(iban):
            return (iban[4:] + iban[:4]).translate(LETTERS)

        def __generate_iban_check_digits(iban):
            number_iban = __number_iban(iban[:2] + '00' + iban[4:])
            return '{:0>2}'.format(98 - (int(number_iban) % 97))

        def __valid_iban(iban):
            return int(__number_iban(iban)) % 97 == 1

        return __generate_iban_check_digits(
            self.text) == self.text[2:4] and __valid_iban(self.text)
