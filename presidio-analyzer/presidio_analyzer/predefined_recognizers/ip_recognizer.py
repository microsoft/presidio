from presidio_analyzer import Pattern, PatternRecognizer


# pylint: disable=line-too-long,abstract-method
class IpRecognizer(PatternRecognizer):
    """
    Recognizes IP address using regex
    """

    PATTERNS = [
        Pattern(
            "IPv4",
            r"\b(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",  # noqa: E501
            0.6,
        ),
        Pattern(
            "IPv6",
            r"\s*(?!.*::.*::)(?:(?!:)|:(?=:))(?:[0-9a-f]{0,4}(?:(?<=::)|(?<!::):)){6}(?:[0-9a-f]{0,4}(?:(?<=::)|(?<!::):)[0-9a-f]{0,4}(?:(?<=::)|(?<!:)|(?<=:)(?<!::):)|(?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\.(?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)){3})\s*",  # noqa: E501
            0.6,
        ),
    ]

    CONTEXT = ["ip", "ipv4", "ipv6"]

    def __init__(
        self,
        patterns=None,
        context=None,
        supported_language="en",
        supported_entity="IP_ADDRESS",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
