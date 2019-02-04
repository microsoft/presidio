from analyzer import Pattern
from analyzer import PatternRecognizer
import tldextract

DOMAIN_REGEX = r'\b(((([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,86}[a-zA-Z0-9]))\.(([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,73}[a-zA-Z0-9]))\.(([a-zA-Z0-9]{2,12}\.[a-zA-Z0-9]{2,12})|([a-zA-Z0-9]{2,25})))|((([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,162}[a-zA-Z0-9]))\.(([a-zA-Z0-9]{2,12}\.[a-zA-Z0-9]{2,12})|([a-zA-Z0-9]{2,25}))))\b'  # noqa: E501'  # noqa: E501
DOMAIN_CONTEXT = ["domain", "ip"]


class DomainRecognizer(PatternRecognizer):
    """
    Recognizes domain names using regex
    """

    def __init__(self):
        patterns = [Pattern('Domain ()', 0.5, DOMAIN_REGEX)]
        super().__init__(supported_entities=["DOMAIN_NAME"], patterns=patterns, context=DOMAIN_CONTEXT)

    def validate_pattern_logic(self, text, pattern_result):
        result = tldextract.extract(text)
        pattern_result.score = 1.0 if result.fqdn is not '' else 0
        return pattern_result
