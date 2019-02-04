from analyzer import Pattern
from analyzer import PatternRecognizer

ITIN_VERY_WEAK_REGEX = r'(\b(9\d{2})[- ]{1}((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))(\d{4})\b)|(\b(9\d{2})((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))[- ]{1}(\d{4})\b)'  # noqa: E501
ITIN_WEAK_REGEX = r'\b(9\d{2})((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))(\d{4})\b'  # noqa: E501
ITIN_MEDIUM_REGEX = r'\b(9\d{2})[- ]{1}((7[0-9]{1}|8[0-8]{1})|(9[0-2]{1})|(9[4-9]{1}))[- ]{1}(\d{4})\b'  # noqa: E501

ITIN_CONTEXT = [
        "individual", "taxpayer", "itin", "tax", "payer", "taxid", "tin"
    ]


class UsItinRecognizer(PatternRecognizer):
    """
    Recognizes US ITIN (Individual Taxpayer Identification Number) using regex
    """

    def __init__(self):
        patterns = [Pattern('Itin (very weak)', 0.05, ITIN_VERY_WEAK_REGEX),
                    Pattern('Itin (weak)', 0.3, ITIN_WEAK_REGEX),
                    Pattern('Itin (medium)', 0.5, ITIN_MEDIUM_REGEX)]
        super().__init__(supported_entities=["US_ITIN"], patterns=patterns, context=ITIN_CONTEXT)

