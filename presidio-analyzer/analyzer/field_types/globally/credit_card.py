from field_types import field_type, field_pattern


class CreditCard(field_type.FieldType):
    name = "CREDIT_CARD"
    should_check_checksum = True
    context = [
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

    patterns = []

    # All credit cards - weak pattern is used, since credit cards has checksum
    pattern = field_pattern.FieldPattern()
    pattern.regex = u'((?:(?:\\d{4}[- ]?){3}\\d{4}|\\d{15,16}))(?![\\d])'
    pattern.name = 'All Credit Cards (weak)'
    pattern.strength = 0.3
    patterns.append(pattern)

    # Dinesr credit card - weak pattern is used, since credit cards has
    # checksum
    pattern = field_pattern.FieldPattern()
    pattern.regex = r'\b3(?:0[0-5]|[68][0-9])[0-9]{11}\b'
    pattern.name = 'Diners (weak)'
    pattern.strength = 0.3
    patterns.append(pattern)

    patterns.sort(key=lambda p: p.strength, reverse=True)

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
