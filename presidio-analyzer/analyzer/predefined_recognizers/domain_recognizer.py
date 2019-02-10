from analyzer import Pattern
from analyzer import PatternRecognizer
import tldextract

REGEX = r'\b(((([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,86}[a-zA-Z0-9]))\.(([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,73}[a-zA-Z0-9]))\.(([a-zA-Z0-9]{2,12}\.[a-zA-Z0-9]{2,12})|([a-zA-Z0-9]{2,25})))|((([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,162}[a-zA-Z0-9]))\.(([a-zA-Z0-9]{2,12}\.[a-zA-Z0-9]{2,12})|([a-zA-Z0-9]{2,25}))))\b'  # noqa: E501'  # noqa: E501
CONTEXT = ["domain", "ip"]


class DomainRecognizer(PatternRecognizer):
    """
    Recognizes domain names using regex
    """

    def __init__(self):
        patterns = [Pattern('Domain ()', REGEX, 0.5)]
        super().__init__(supported_entities=["DOMAIN_NAME"], patterns=patterns,
                         context=CONTEXT)

    def validate_result(self, text, pattern_result):
        result = tldextract.extract(text)
        pattern_result.score = 1.0 if result.fqdn is not '' else 0
        return pattern_result
