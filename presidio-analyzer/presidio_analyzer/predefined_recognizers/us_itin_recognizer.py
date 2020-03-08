from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer

# pylint: disable=line-too-long,abstract-method
VERY_WEAK_REGEX = r'(\b(9\d{2})[- ]{1}((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))(\d{4})\b)|(\b(9\d{2})((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))[- ]{1}(\d{4})\b)'  # noqa: E501
WEAK_REGEX = r'\b(9\d{2})((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))(\d{4})\b'  # noqa: E501
MEDIUM_REGEX = r'\b(9\d{2})[- ]{1}((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))[- ]{1}(\d{4})\b'  # noqa: E501

CONTEXT = [
    "individual", "taxpayer", "itin", "tax", "payer", "taxid", "tin"
]


class UsItinRecognizer(PatternRecognizer):
    """
    Recognizes US ITIN (Individual Taxpayer Identification Number) using regex
    """

    def __init__(self):
        patterns = [Pattern('Itin (very weak)', VERY_WEAK_REGEX, 0.05),
                    Pattern('Itin (weak)', WEAK_REGEX, 0.3),
                    Pattern('Itin (medium)', MEDIUM_REGEX, 0.5)]
        super().__init__(supported_entity="US_ITIN", patterns=patterns,
                         context=CONTEXT)
