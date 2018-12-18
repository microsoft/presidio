from field_types import field_type, field_regex_pattern


class Ip(field_type.FieldType):
    name = "IP_ADDRESS"
    context = ["ip", "ipv4", "ipv6"]

    patterns = []

    pattern = field_regex_pattern.RegexFieldPattern()
    pattern.regex = r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'  # noqa: E501
    pattern.name = 'IPv4'
    pattern.strength = 0.6
    patterns.append(pattern)

    pattern = field_regex_pattern.RegexFieldPattern()
    pattern.regex = r'\s*(?!.*::.*::)(?:(?!:)|:(?=:))(?:[0-9a-f]{0,4}(?:(?<=::)|(?<!::):)){6}(?:[0-9a-f]{0,4}(?:(?<=::)|(?<!::):)[0-9a-f]{0,4}(?:(?<=::)|(?<!:)|(?<=:)(?<!::):)|(?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)){3})\s*'  # noqa: E501
    pattern.name = 'IPv6'
    pattern.strength = 0.6
    patterns.append(pattern)

    patterns.sort(key=lambda p: p.strength, reverse=True)
