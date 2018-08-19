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
    pattern.regex = r"\b(?!(https:\/\/|http:\/\/|www\.|mailto:|smtp:|ftp:\/\/|ftps:\/\/))(((([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,86}[a-zA-Z0-9]))\.(([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,73}[a-zA-Z0-9]))\.(([a-zA-Z0-9]{2,12}\.[a-zA-Z0-9]{2,12})|([a-zA-Z0-9]{2,25})))|((([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,162}[a-zA-Z0-9]))\.(([a-zA-Z0-9]{2,12}\.[a-zA-Z0-9]{2,12})|([a-zA-Z0-9]{2,25}))))\b"
    pattern.name = 'Domain ()'
    pattern.strength = 0.5

    patterns.append(pattern)

    def check_checksum(self):
        result = tldextract.extract(self.text)
        if result.fqdn is not '':
            return True
        else:
            return False
