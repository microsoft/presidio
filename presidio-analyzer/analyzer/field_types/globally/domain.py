import tldextract
from field_types import field_type, field_pattern


class Domain(field_type.FieldType):
    name = "DOMAIN_NAME"
    should_check_checksum = True
    context = [
        "domain",
        "ip"
    ]

    patterns = []

    # Basic pattern, since domain has a checksum function
    pattern = field_pattern.FieldPattern()
    pattern.regex = r"(([\da-zA-Z])([_\w-]{,62})\.){,127}(([\da-zA-Z])[_\w-]{,61})?([\da-zA-Z]\.((xn\-\-[a-zA-Z\d]+)|([a-zA-Z\d]{2,})))"
    pattern.name = 'Domain ()'
    pattern.strength = 0.5

    patterns.append(pattern)

    def check_checksum(self):
        result = tldextract.extract(self.text)
        if result.fqdn is not '':
            return True
        else:
            return False
