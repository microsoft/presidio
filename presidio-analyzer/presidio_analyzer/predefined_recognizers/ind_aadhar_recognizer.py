from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer

#
# Ref: https://en.wikipedia.org/wiki/Aadhaar
REGEX = r'\b[2-9]\d{3}[ \-]*\d{4}[ \-]*\d{4}(?!=\d)\b'
CONTEXT = ["aadhar","adhar","UID","India","UIDAI","card","personal","identification","number"]


class INDAadharRecognizer(PatternRecognizer):
    """
    Recognizes Indian Aadhar card number using regex
    """

    def __init__(self):
        patterns = [Pattern('Aadhar Card ', REGEX, 0.55) ]
        super().__init__(supported_entity="IND_AADHAR_CARD", patterns=patterns,
                         context=CONTEXT)

