from analyzer import Pattern
from analyzer import PatternRecognizer
import string

IP_V4_REGEX = r'\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'  # noqa: E501
IP_V6_REGEX = r'\s*(?!.*::.*::)(?:(?!:)|:(?=:))(?:[0-9a-f]{0,4}(?:(?<=::)|(?<!::):)){6}(?:[0-9a-f]{0,4}(?:(?<=::)|(?<!::):)[0-9a-f]{0,4}(?:(?<=::)|(?<!:)|(?<=:)(?<!::):)|(?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)){3})\s*'  # noqa: E501

IP_CONTEXT = ["ip", "ipv4", "ipv6"]


class IpRecognizer(PatternRecognizer):
    """
    Recognizes IP address using regex
    """

    def __init__(self):
        patterns = [Pattern('IPv4', 0.6, IP_V4_REGEX), Pattern('IPv6', 0.6, IP_V6_REGEX)]
        super().__init__(supported_entities=["IP_ADDRESS"], patterns=patterns, context=IP_CONTEXT)

