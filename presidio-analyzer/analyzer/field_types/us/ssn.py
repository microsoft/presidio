from field_types import field_type


class UsSsn(field_type.FieldType):
    name = "US_SSN"
    context = [
        "social",
        "security",
        "soc",
        "sec",
        "ssn",
        "ssns",
        "ssn#",
        "ss#",
        "ssid"]
    regexes = {
        "ssn":
        r'([0-9]{3})-?([0-9]{2})-?([0-9]{4})\b',
    }
