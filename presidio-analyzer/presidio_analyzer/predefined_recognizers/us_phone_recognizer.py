from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer

# List from https://ntsi.com/drivers-license-format/
# ---------------

# WA Driver License number is relatively unique as it also
# includes '*' chars.
# However it can also be 12 letters which makes every 12 letter'
# word a match. Therefore we split WA driver license
# regex: r'\b([A-Z][A-Z0-9*]{11})\b' into two regexes
# With different weights, one to indicate letters only and
# one to indicate at least one digit or one '*'

# pylint: disable=line-too-long,abstract-method
CONTEXT = ["phone", "number", "telephone", "cell", "mobile", "call"]


class UsPhoneRecognizer(PatternRecognizer):
    """
    Recognizes US Phone numbers using regex
    """

    STRONG_REGEX_SCORE = 0.7
    MEDIUM_REGEX_SCORE = 0.5
    WEAK_REGEX_SCORE = 0.05

    STRONG_REGEX = \
        r'(\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|d{3}[-\.\s]\d{3}[-\.\s]\\d{4})'
    MEDIUM_REGEX = r'\b(\d{3}[-\.\s]\d{3}[-\.\s]??\d{4})\b'
    WEAK_REGEX = r'(\b\d{10}\b)'

    def __init__(self):
        patterns = [Pattern('Phone (strong)',
                            UsPhoneRecognizer.STRONG_REGEX,
                            UsPhoneRecognizer.STRONG_REGEX_SCORE),
                    Pattern('Phone (medium)',
                            UsPhoneRecognizer.MEDIUM_REGEX,
                            UsPhoneRecognizer.MEDIUM_REGEX_SCORE),
                    Pattern('Phone (weak)',
                            UsPhoneRecognizer.WEAK_REGEX,
                            UsPhoneRecognizer.WEAK_REGEX_SCORE)]
        super().__init__(supported_entity="PHONE_NUMBER",
                         patterns=patterns, context=CONTEXT)
