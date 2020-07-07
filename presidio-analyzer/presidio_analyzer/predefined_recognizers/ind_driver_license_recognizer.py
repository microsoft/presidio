from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer

#
# Ref: https://en.wikipedia.org/wiki/Driving_licence_in_India
REGEX = r'\b(AN|AP|AR|AS|BR|CH|DN|DD|DL|GA|GJ|HR|HP|JK|KA|KL|LD|MP|MH|MN|ML|MZ|NL|OR|PY|PN|RJ|SK|TN|TR|UP|WB|an|ap|ar|as|br|ch|dn|dd|dl|ga|gj|hr|hp|jk|ka|kl|ld|mp|mh|mn|ml|mz|nl|or|py|pn|rj|sk|tn|tr|up|wb){1}[ -]*\d{2}[ -]*(19|20)\d{2}[ -]*\d{7}\b'

CONTEXT = ["driving","license","india","driver", "license", "permit", "lic", "identification",
    "dl", "dls", "cdls", "id", "lic#", "driving"]


class INDLicenseRecognizer(PatternRecognizer):
    """
    Recognizes Indian Driving License number using regex
    """

    def __init__(self):
        patterns = [Pattern('Driver License ', REGEX, 0.7) ]
        super().__init__(supported_entity="IND_DRIVER_LICENSE", patterns=patterns,
                         context=CONTEXT)
