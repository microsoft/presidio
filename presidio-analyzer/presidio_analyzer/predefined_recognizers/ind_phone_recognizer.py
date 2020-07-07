from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer

#Reference: https://en.wikipedia.org/wiki/Telephone_numbers_in_India

CONTEXT = ["phone", "number", "telephone", "cell", "mobile", "call"]
Landline_Regex = r'\b[\(\+]*(91)*[ \-\)\(]*0\d{2}[ \-\)\(]*\d[ \-\)\(]*\d{3}[ \-\)\(]*\d{4}[\)]*\b'
Mobile_Regex = r'\b[\(\+]*(91)*[\(\) \-]*[6-9]\d{2}[\(\) \-]*\d{2}[\(\) \-]*\d[\(\) \-]*\d{4}[\)]*\b'
Landline_Regex_Score = 0.55
Mobile_Regex_Score = 0.55


class INDPhoneRecognizer(PatternRecognizer):
    "Recognizes Indian Phone numbers using Regex"

    def __init__(self):
        patterns = [Pattern('Phone (India Landline)', Landline_Regex,
                            Landline_Regex_Score),
                    Pattern('Phone (India Mobile)', Mobile_Regex,
                            Mobile_Regex_Score)]
        super().__init__(supported_entity = "IND_PHONE_NUMBER", patterns = patterns, context = CONTEXT)
