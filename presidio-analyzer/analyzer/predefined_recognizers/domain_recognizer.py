from analyzer import Pattern
from analyzer import PatternRecognizer
from analyzer.entity_recognizer import EntityRecognizer
import tldextract

REGEX = r'\b(((([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,86}[a-zA-Z0-9]))\.(([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,73}[a-zA-Z0-9]))\.(([a-zA-Z0-9]{2,12}\.[a-zA-Z0-9]{2,12})|([a-zA-Z0-9]{2,25})))|((([a-zA-Z0-9])|([a-zA-Z0-9][a-zA-Z0-9\-]{0,162}[a-zA-Z0-9]))\.(([a-zA-Z0-9]{2,12}\.[a-zA-Z0-9]{2,12})|([a-zA-Z0-9]{2,25}))))\b'  # noqa: E501'  # noqa: E501
CONTEXT = ["domain", "ip"]


class DomainRecognizer(PatternRecognizer):
    """
    Recognizes domain names using regex
    """

    def __init__(self):
        patterns = [Pattern('Domain ()', REGEX, 0.5)]
        super().__init__(supported_entity="DOMAIN_NAME", patterns=patterns,
                         context=CONTEXT)

    def validate_result(self, text, pattern_result):
        result = tldextract.extract(text)
        if result.fqdn != '':
            pattern_result.score = EntityRecognizer.MAX_SCORE
        else:
            pattern_result.score = EntityRecognizer.MIN_SCORE
        return pattern_result
