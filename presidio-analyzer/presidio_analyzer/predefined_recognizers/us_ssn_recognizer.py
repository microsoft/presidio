from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer
# pylint: disable=line-too-long,abstract-method

# List from https://ntsi.com/drivers-license-format/
# ---------------

# WA Driver License number is relatively unique as it also
# includes '*' chars.
# However it can also be 12 letters which makes every 12 letter'
# word a match. Therefore we split WA driver license
# regex: r'\b([A-Z][A-Z0-9*]{11})\b' into two regexes
# With different weights, one to indicate letters only and
# one to indicate at least one digit or one '*'

VERY_WEAK_REGEX = r'\b(([0-9]{5})-([0-9]{4})|([0-9]{3})-([0-9]{6}))\b'
WEAK_REGEX = r'\b[0-9]{9}\b'
MEDIUM_REGEX = r'\b([0-9]{3})-([0-9]{2})-([0-9]{4})\b'

CONTEXT = [
    "social",
    "security",
    # "sec", # Task #603: Support keyphrases ("social sec")
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
        patterns = [Pattern('SSN (very weak)', VERY_WEAK_REGEX, 0.05),
                    Pattern('SSN (weak)', WEAK_REGEX, 0.3),
                    Pattern('SSN (medium)', MEDIUM_REGEX, 0.5)]
        super().__init__(supported_entity="US_SSN", patterns=patterns,
                         context=CONTEXT)
