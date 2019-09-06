from analyzer import Pattern
from analyzer import PatternRecognizer

# pylint: disable=line-too-long,abstract-method
# Weak pattern: all FIN number start with G or S and end with a character, e.g., G3377788L
VERY_WEAK_REGEX = r'(\b[0-9]{7}\b)'
WEAK_REGEX = r'(\b[a-z,A-Z][0-9]{7}[a-z,A-Z]\b)'
MEDIUM_REGEX = r'(\b[s,t,f,g][0-9]{7}[a-z,A-Z]\b)'

CONTEXT = ["fin", "fin#", "nric", "nric#"]


class SgFinRecognizer(PatternRecognizer):
    """
    Recognizes SG FIN/NRIC number using regex
    """

    def __init__(self):
        patterns = [Pattern('Nric (very weak) ', VERY_WEAK_REGEX, 0.04),
            Pattern('Nric (weak) ', WEAK_REGEX, 0.2),
            Pattern('Nric (medium) ', MEDIUM_REGEX, 0.4),
]
        super().__init__(supported_entity="SG_NRIC_FIN", patterns=patterns,
                         context=CONTEXT)
