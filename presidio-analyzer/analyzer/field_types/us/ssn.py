from field_types import field_type, field_regex_pattern


class UsSsn(field_type.FieldType):
    name = "US_SSN"
    context = [
        "social",
        "security",
        # "sec", TODO: add keyphrase support in "social sec"
        "ssn",
        "ssns",
        "ssn#",
        "ss#",
        "ssid"
    ]

    # Master Regex: r'\b([0-9]{3})-?([0-9]{2})-?([0-9]{4})\b'
    patterns = []

    pattern = field_regex_pattern.RegexFieldPattern()
    pattern.regex = r'\b(([0-9]{5})-([0-9]{4})|([0-9]{3})-([0-9]{6}))\b'
    pattern.name = 'SSN (very weak)'
    pattern.strength = 0.05
    patterns.append(pattern)

    pattern = field_regex_pattern.RegexFieldPattern()
    pattern.regex = r'\b[0-9]{9}\b'
    pattern.name = 'SSN (weak)'
    pattern.strength = 0.3
    patterns.append(pattern)

    pattern = field_regex_pattern.RegexFieldPattern()
    pattern.regex = r'\b([0-9]{3})-([0-9]{2})-([0-9]{4})\b'
    pattern.name = 'SSN (medium)'
    pattern.strength = 0.5
    patterns.append(pattern)

    patterns.sort(key=lambda p: p.strength, reverse=True)
