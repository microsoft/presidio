from field_types import field_type, field_regex_pattern


class UkNhs(field_type.FieldType):
    name = "UK_NHS"
    should_check_checksum = True
    context = [
        "national health service", "nhs", "health services authority",
        "health authority"
    ]

    patterns = []

    pattern = field_regex_pattern.RegexFieldPattern()
    pattern.regex = r'\b([0-9]{3})[- ]?([0-9]{3})[- ]?([0-9]{4})\b'
    pattern.name = 'NHS (medium)'
    pattern.strength = 0.5
    patterns.append(pattern)

    patterns.sort(key=lambda p: p.strength, reverse=True)

    def __sanitize_value(self):
        self.sanitized_value = self.text.replace('-', '').replace(' ', '')

    def check_checksum(self):
        self.__sanitize_value()

        multiplier = 10
        total = 0
        for c in self.sanitized_value:
            val = int(c)
            total = total + val * multiplier
            multiplier = multiplier - 1

        remainder = total % 11
        check_digit = 11 - remainder
        if check_digit == 11:
            return True

        return False
