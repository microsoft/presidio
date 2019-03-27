import tldextract

from analyzer import Pattern
from analyzer import PatternRecognizer
from analyzer.entity_recognizer import EntityRecognizer

# pylint: disable=line-too-long
REGEX = r"\b((([!#$%&'*+\-/=?^_`{|}~\w])|([!#$%&'*+\-/=?^_`{|}~\w][!#$%&'*+\-/=?^_`{|}~\.\w]{0,}[!#$%&'*+\-/=?^_`{|}~\w]))[@]\w+([-.]\w+)*\.\w+([-.]\w+)*)\b"  # noqa: E501
CONTEXT = ["email"]


class EmailRecognizer(PatternRecognizer):
    """
    Recognizes email addresses using regex
    """

    def __init__(self):
        patterns = [Pattern('Email (Medium)', REGEX, 0.5)]
        super().__init__(supported_entity="EMAIL_ADDRESS",
                         patterns=patterns, context=CONTEXT)

    def validate_result(self, pattern_text, pattern_result):
        result = tldextract.extract(pattern_text)

        if result.fqdn != '':
            pattern_result.score = EntityRecognizer.MAX_SCORE
        else:
            pattern_result.score = EntityRecognizer.MIN_SCORE
        return pattern_result
