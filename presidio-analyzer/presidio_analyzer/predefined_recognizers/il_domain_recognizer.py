import tldextract

from presidio_analyzer import Pattern, PatternRecognizer

# pylint: disable=line-too-long
IL_DOMAIN_REGEX = u'(www.)?[\u05D0-\u05EA]{2,63}.co.il'  # noqa: E501'  # noqa: E501
CONTEXT = ["domain", "ip"]


class ILDomainRecognizer(PatternRecognizer):
    """
    Recognizes hebrew domain names using regex
    """

    def __init__(self):
        patterns = [Pattern('IL Domain', IL_DOMAIN_REGEX, 0.5)]
        super().__init__(supported_entity="IL_DOMAIN_NAME", patterns=patterns,
                         context=CONTEXT, supported_language='he')

    def validate_result(self, pattern_text):
        result = tldextract.extract(pattern_text)
        return result.fqdn != ''
