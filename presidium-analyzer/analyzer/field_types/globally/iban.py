import string
from field_types import field_type


class Iban(field_type.FieldType):
    name = "IBAN"
    context = ["iban"]
    should_check_checksum = True
    regexes = {"iban": u'^DE\d{2}\s?([0-9a-zA-Z]{4}\s?){4}[0-9a-zA-Z]{2}$'}

    def check_checksum(self):
        LETTERS = {
            ord(d): str(i)
            for i, d in enumerate(string.digits + string.ascii_uppercase)
        }

        def ___number_iban(iban):
            return (iban[4:] + iban[:4]).translate(LETTERS)

        def __generate_iban_check_digits(iban):
            number_iban = __number_iban(iban[:2] + '00' + iban[4:])
            return '{:0>2}'.format(98 - (int(number_iban) % 97))

        def __valid_iban(iban):
            return int(_number_iban(iban)) % 97 == 1

        return __generate_iban_check_digits(
            self.text) == unchecked_iban[2:4] and __valid_iban(self.text)
