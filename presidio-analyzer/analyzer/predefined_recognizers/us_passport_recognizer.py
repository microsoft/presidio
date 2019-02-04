from analyzer import Pattern
from analyzer import PatternRecognizer

# Weak pattern: all passport numbers are a weak match, e.g., 14019033
US_PASSPORT_VERY_WEAK_REGEX = r'(\b[0-9]{9}\b)'

US_PASSPORT_CONTEXT = [
    "us", "united", "states", "passport", "number", "passport#", "travel",
    "document"
]


class UsPassportRecognizer(PatternRecognizer):
    """
    Recognizes US Passport number using regex
    """

    def __init__(self):
        patterns = [Pattern('Passport (very weak)', 0.05, US_PASSPORT_VERY_WEAK_REGEX)]
        super().__init__(supported_entities=["US_PASSPORT"], patterns=patterns, context=US_PASSPORT_CONTEXT)
