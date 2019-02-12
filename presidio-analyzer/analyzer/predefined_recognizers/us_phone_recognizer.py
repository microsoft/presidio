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

STRONG_REGEX = r'(\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|d{3}[-\.\s]\d{3}[-\.\s]\d{4})'  # noqa: E501
MEDIUM_REGEX = r'\b(\d{3}[-\.\s]\d{3}[-\.\s]??\d{4})\b'
WEAK_REGEX = r'(\b\d{10}\b)'

CONTEXT = ["phone", "number", "telephone", "cell", "mobile", "call"]


class UsPhoneRecognizer(PatternRecognizer):
    """
    Recognizes US Phone numbers using regex
    """

    def __init__(self):
        patterns = [Pattern('Phone (strong)', STRONG_REGEX, 0.7),
                    Pattern('Phone (medium)', MEDIUM_REGEX, 0.5),
                    Pattern('Phone (weak)', WEAK_REGEX, 0.05)]
        super().__init__(supported_entity="PHONE_NUMBER",
                         patterns=patterns, context=CONTEXT)
