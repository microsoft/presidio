import re

from field_types import field_type


class Email(field_type.FieldType):
    name = "EMAIL"
    context = []
    regexes = {
        "email": re.compile(
            r"([a-z0-9!#$%&'*+\/=?^_`{|.}~-]+@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE)
    }
