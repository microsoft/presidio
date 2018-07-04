from field_types import field_type


class CreditCard(field_type.FieldType):
    name = "CREDIT_CARD"
    should_check_checksum = True
    context = ["credit", "card"]
    regexes = {
        # "cd": r'\b(?:\d[ -]*?){13,16}\b'
        "creditcard1": u'((?:(?:\\d{4}[- ]?){3}\\d{4}|\\d{15,16}))(?![\\d])',
        # "creditcard2":
        # u'(4\d{3})(-?|\040*)(\d{4}(-?|\040*?)){3}',
    }

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

    def __santize_value(self):
        self.sanitized_value = self.text.replace('-', '').replace(' ', '')

    def check_checksum(self):
        self.__santize_value()
        return self.__luhn_checksum() == 0
