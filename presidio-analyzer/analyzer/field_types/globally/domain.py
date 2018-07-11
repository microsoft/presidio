import validators
from field_types import field_type


class Domain(field_type.FieldType):
    name = "DOMAIN_NAME"
    should_check_checksum = True
    context = []
    regexes = {
        "domain":
        r"(([\da-zA-Z])([_\w-]{,62})\.){,127}(([\da-zA-Z])[_\w-]{,61})?([\da-zA-Z]\.((xn\-\-[a-zA-Z\d]+)|([a-zA-Z\d]{2,})))"
    }

    def check_checksum(self):
        return validators.domain(self.text)
