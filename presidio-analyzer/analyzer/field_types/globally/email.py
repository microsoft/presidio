import tldextract
from field_types import field_type, field_pattern


class Email(field_type.FieldType):
    name = "EMAIL_ADDRESS"
    should_check_checksum = True
    context = [
        "email"
    ]

    patterns = []

    pattern = field_pattern.FieldPattern()
    pattern.regex = r"\b((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)\b"
    pattern.name = 'Email (Medium)'
    pattern.strength = 0.5
    patterns.append(pattern)

    def check_checksum(self):
        result = tldextract.extract(self.text)
        if result.fqdn is not '':
            return True
        else:
            return False
