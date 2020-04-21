import tldextract

from presidio_analyzer import Pattern, PatternRecognizer


class DomainRecognizer(PatternRecognizer):
    """
    Recognizes domain names using regex
    """

    # pylint: disable=line-too-long
    PATTERN_GROUPS = [
        (
            "Domain ()",
            r"\b(((([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,86}[a-zA-Z0-9]))\.(([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,73}[a-zA-Z0-9]))\.(([a-zA-Z0-9]{2,12}\.[a-zA-Z0-9]{2,12})|([a-zA-Z0-9]{2,25})))|((([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,162}[a-zA-Z0-9]))\.(([a-zA-Z0-9]{2,12}\.[a-zA-Z0-9]{2,12})|([a-zA-Z0-9]{2,25}))))\b",  # noqa: E501'  # noqa: E501
            0.5,
        ),
    ]

    CONTEXT = ["domain", "ip"]

    def __init__(
        self,
        pattern_groups=None,
        context=None,
        supported_language="en",
        supported_entity="DOMAIN_NAME",
    ):
        pattern_groups = pattern_groups if pattern_groups else self.PATTERN_GROUPS
        context = context if context else self.CONTEXT
        patterns = [Pattern(*pattern_group) for pattern_group in pattern_groups]
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text):
        result = tldextract.extract(pattern_text)
        return result.fqdn != ""
