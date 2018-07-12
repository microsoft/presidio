import validators
from field_types import field_type


class Email(field_type.FieldType):
    name = "EMAIL"
    should_check_checksum = True
    context = []
    regexes = {
        "email":
        r"([a-z0-9!#$%&'*+\/=?^_`{|.}~-]+@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"
    }

    def check_checksum(self):
        return validators.email(self.text)
