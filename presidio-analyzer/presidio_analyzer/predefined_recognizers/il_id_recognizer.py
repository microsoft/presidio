from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer
# pylint: disable=line-too-long,abstract-method

ISRAELI_ID_REGEX = r'\b[0-9]{7,10}\b'

# Todo (Task: TBD): fix context for unsupported languages
CONTEXT = [
    "תעודה",
    "זהות",
    "תעודת",
    "ת.ז"
]


class ILIDRecognizer(PatternRecognizer):
    """
    Recognizes an Israeli ID using regex
    """

    def __init__(self):
        patterns = [Pattern('israeli id simple regex', ISRAELI_ID_REGEX, 0.2)]
        super().__init__(supported_entity="IL_ID", patterns=patterns,
                         context=CONTEXT, supported_language='he')
