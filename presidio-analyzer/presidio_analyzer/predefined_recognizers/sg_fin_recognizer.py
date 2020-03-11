from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer

# pylint: disable=line-too-long,abstract-method
# Weak pattern: all FIN number start with "S", "T", "F" or "G"
# and ends with a character, e.g., G3311100L
# Ref: https://en.wikipedia.org/wiki/National_Registration_Identity_Card
WEAK_REGEX = r'(\b[a-z,A-Z][0-9]{7}[a-z,A-Z]\b)'
MEDIUM_REGEX = r'(\b[stfgSTFG][0-9]{7}[a-z,A-Z]\b)'

CONTEXT = ["fin", "fin#", "nric", "nric#"]


class SgFinRecognizer(PatternRecognizer):
    """
    Recognizes SG FIN/NRIC number using regex
    """

    def __init__(self):
        patterns = [Pattern('Nric (weak) ', WEAK_REGEX, 0.3),
                    Pattern('Nric (medium) ', MEDIUM_REGEX, 0.5), ]
        super().__init__(supported_entity="SG_NRIC_FIN", patterns=patterns,
                         context=CONTEXT)
