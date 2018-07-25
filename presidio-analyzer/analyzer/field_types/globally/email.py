import validators
from field_types import field_type, field_pattern


class Email(field_type.FieldType):
    name = "EMAIL"
    should_check_checksum = True
    context = [
        "email"
    ]

    patterns = []

    pattern = field_pattern.FieldPattern()
    pattern.regex = r"([a-z0-9!#$%&'*+\/=?^_`{|.}~-]+@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"
    pattern.name = 'Email (Medium)'
    pattern.strength = 0.5
    patterns.append(pattern)


    def check_checksum(self):
        return validators.email(self.text)
