from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer

#
# Ref: https://en.wikipedia.org/wiki/Indian_passport
WEAK_REGEX = r'\b[a-zA-Z]\d{7}\b'

CONTEXT = ["passport","india","visa","travel","document"]


class INDPassportRecognizer(PatternRecognizer):
    """
    Recognizes Indian Passport number using regex
    """

    def __init__(self):
        patterns = [Pattern('Passport ', WEAK_REGEX, 0.3) ]
        super().__init__(supported_entity="IND_PASSPORT", patterns=patterns,
                         context=CONTEXT)
