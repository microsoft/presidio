from analyzer import Pattern
from analyzer import PatternRecognizer

# pylint: disable=line-too-long,abstract-method
# Weak pattern: all passport numbers are a weak match, e.g., 14019033
VERY_WEAK_REGEX = r'(\b[0-9]{9}\b)'

CONTEXT = [
    "passport", "passport#"
]


class UsPassportRecognizer(PatternRecognizer):
    """
    Recognizes US Passport number using regex
    """

    def __init__(self):
        patterns = [Pattern('Passport (very weak)', VERY_WEAK_REGEX, 0.2)]
        super().__init__(supported_entity="US_PASSPORT", patterns=patterns,
                         context=CONTEXT)
