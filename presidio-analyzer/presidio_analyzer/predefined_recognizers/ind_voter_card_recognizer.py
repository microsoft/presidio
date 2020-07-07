from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer

#
# Ref: https://en.wikipedia.org/wiki/Driving_licence_in_India
REGEX = r'\b([a-zA-Z]){3}([0-9]){7}?\b'

CONTEXT = ["voter","vote","identity","card","epic"]


class INDEPICRecognizer(PatternRecognizer):
    """
    Recognizes Indian voter card number using regex
    """

    def __init__(self):
        patterns = [Pattern('Voter card(EPIC) number ', REGEX, 0.3) ]
        super().__init__(supported_entity="IND_VOTER_CARD", patterns=patterns,
                         context=CONTEXT)

