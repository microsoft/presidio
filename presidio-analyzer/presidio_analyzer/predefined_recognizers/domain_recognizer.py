import tldextract

from presidio_analyzer import Pattern, PatternRecognizer


class DomainRecognizer(PatternRecognizer):
    """
    Recognizes domain names using regex
    """

    # pylint: disable=line-too-long
    PATTERNS = [
        Pattern(
            "Domain ()",
            r"\b(((([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,86}[a-zA-Z0-9]))\.(([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,73}[a-zA-Z0-9]))\.(([a-zA-Z0-9]{2,12}\.[a-zA-Z0-9]{2,12})|([a-zA-Z0-9]{2,25})))|((([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,162}[a-zA-Z0-9]))\.(([a-zA-Z0-9]{2,12}\.[a-zA-Z0-9]{2,12})|([a-zA-Z0-9]{2,25}))))\b",  # noqa: E501'  # noqa: E501
            0.5,
        ),
    ]

    CONTEXT = ["domain", "ip"]

    def __init__(
        self,
        patterns=None,
        context=None,
        supported_language="en",
        supported_entity="DOMAIN_NAME",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

    def validate_result(self, pattern_text):
        result = tldextract.extract(pattern_text)
        return result.fqdn != ""
