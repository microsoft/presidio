from analyzer import Pattern
from analyzer import PatternRecognizer
import tldextract

EMAIL_REGEX = r"\b((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)\b"  # noqa: E501
EMAIL_CONTEXT = ["email"]


class EmailRecognizer(PatternRecognizer):
    """
    Recognizes email addresses using regex
    """

    def __init__(self):
        patterns = [Pattern('Email (Medium)', 0.5, EMAIL_REGEX)]
        super().__init__(supported_entities=["EMAIL_ADDRESS"], patterns=patterns, context=EMAIL_CONTEXT)

    def validate_result(self, text, pattern_result):
        result = tldextract.extract(text)

        pattern_result.score = 1.0 if result.fqdn is not '' else 0
        return pattern_result

