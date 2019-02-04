from analyzer import Pattern
from analyzer import PatternRecognizer

# List from https://ntsi.com/drivers-license-format/
# ---------------

# WA Driver License number is relatively unique as it also
# includes '*' chars.
# However it can also be 12 letters which makes every 12 letter'
# word a match. Therefore we split WA driver license
# regex: r'\b([A-Z][A-Z0-9*]{11})\b' into two regexes
# With different weights, one to indicate letters only and
# one to indicate at least one digit or one '*'

PHONE_STRONG_REGEX = r'(\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|d{3}[-\.\s]\d{3}[-\.\s]\d{4})'  # noqa: E501
PHONE_MEDIUM_REGEX = r'\b(\d{3}[-\.\s]\d{3}[-\.\s]??\d{4})\b'
PHONE_WEAK_REGEX = r'(\b\d{10}\b)'

PHONE_CONTEXT = ["phone", "number", "telephone", "cell", "mobile", "call"]


class UsPhoneRecognizer(PatternRecognizer):
    """
    Recognizes US Phone numbers using regex
    """

    def __init__(self):
        patterns = [Pattern('Phone (strong)', 0.7, PHONE_STRONG_REGEX),
                    Pattern('Phone (medium)', 0.5, PHONE_MEDIUM_REGEX),
                    Pattern('Phone (weak)', 0.05, PHONE_WEAK_REGEX)]
        super().__init__(supported_entities=["PHONE_NUMBER"], patterns=patterns, context=PHONE_CONTEXT)

