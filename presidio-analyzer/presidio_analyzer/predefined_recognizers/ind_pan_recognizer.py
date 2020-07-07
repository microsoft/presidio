from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer

#
# Ref: https://www.incometaxindia.gov.in/Forms/tps/1.Permanent%20Account%20Number%20(PAN).pdf
REGEX = r'\b[a-zA-Z]{3}(P|C|H|A|B|G|J|L|F|T|p|c|h|a|b|g|j|l|f|t){1}[a-zA-Z]\d{4}[a-zA-Z]\b'

CONTEXT = ["permanent","account","number","PAN","card","india","pan"]


class INDPANRecognizer(PatternRecognizer):
    """
    Recognizes Indian Pan Card number using regex
    """

    def __init__(self):
        patterns = [Pattern('PAN Card ', REGEX, 0.5) ]
        super().__init__(supported_entity="IND_PAN_CARD", patterns=patterns,
                         context=CONTEXT)
