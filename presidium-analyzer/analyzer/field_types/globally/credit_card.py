import re

from field_types import field_type


class CreditCard(field_type.FieldType):
    name = "CREDIT_CARD"
    should_check_checksum = True
    context = ["credit", "card"]
    regexes = {
        "creditcard1": re.compile(
            u'((?:(?:\\d{4}[- ]?){3}\\d{4}|\\d{15,16}))(?![\\d])'),
        "creditcard2": re.compile(
            u'((?:(?:\\d{4}[- ]?){6}\\d{5}|\\d{15,16}))(?![\\d])')

    }

    def check_checksum(self):
        """determines whether the card number is valid."""
        n = self.value.replace("-", "")
        if not n.isdigit():
            return False

        return int(n[-1]) == self.__get_check_digit(n[:-1])

    def __get_check_digit(self, unchecked):
        """returns the check digit of the card number."""
        digits = self.__digits_of__(unchecked)
        checksum = sum(self.__even_digits__(unchecked)) + sum([
            sum(self.__digits_of__(2 * d)) for d in self.__odd_digits__(unchecked)])
        return 9 * checksum % 10

    def __digits_of__(self, number):
        """gets the digits of a number in a list."""
        return [int(d) for d in str(number)]

    def __even_digits__(self, number):
        """gets a list of digits at even indexes of the number starting at the last
        digit and counting from 1."""
        return list(map(int, str(number)[-2::-2]))

    def __odd_digits__(self, number):
        """gets a list of digits at odd indexes of the number starting at the last
        digit and counting from 1."""
        return list(map(int, str(number)[-1::-2]))
