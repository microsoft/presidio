from email.utils import parseaddr
from field_types import field_type


class Email(field_type.FieldType):
    name = "EMAIL"
    context = ["email", "address"]
    regexes = {
        "email":
        r"([a-z0-9!#$%&'*+\/=?^_`{|.}~-]+@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"
    }
