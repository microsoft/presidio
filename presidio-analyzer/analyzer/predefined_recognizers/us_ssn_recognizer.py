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

SSN_VERY_WEAK_REGEX = r'\b(([0-9]{5})-([0-9]{4})|([0-9]{3})-([0-9]{6}))\b'
SSN_WEAK_REGEX = r'\b[0-9]{9}\b'
SSN_MEDIUM_REGEX = r'\b([0-9]{3})-([0-9]{2})-([0-9]{4})\b'

US_SSN_CONTEXT = [
        "social",
        "security",
        # "sec", TODO: add keyphrase support in "social sec"
        "ssn",
        "ssns",
        "ssn#",
        "ss#",
        "ssid"
    ]


class UsSsnRecognizer(PatternRecognizer):
    """
    Recognizes US Social Security Number (SSN) using regex
    """

    def __init__(self):
        patterns = [Pattern('SSN (very weak)', 0.05, SSN_VERY_WEAK_REGEX),
                    Pattern('SSN (weak)', 0.3, SSN_WEAK_REGEX),
                    Pattern('SSN (medium)', 0.5, SSN_MEDIUM_REGEX)]
        super().__init__(supported_entities=["US_ITIN"], patterns=patterns, context=US_SSN_CONTEXT)

