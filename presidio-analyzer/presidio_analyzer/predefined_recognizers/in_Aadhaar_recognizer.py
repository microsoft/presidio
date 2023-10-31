from typing import Optional, List, Tuple

from presidio_analyzer import Pattern, PatternRecognizer


class InAadhaarRecognizer(PatternRecognizer):
    """
    Recognizes Indian Aadhaar card number.

    The Aadhaar card is a 12 digit numeric code
    with the last digit being a check digit calculated using a
    modified modulus 10 calculation.
    This recognizer identifies Aadhaar using regex and context words.
    Reference: https://en.wikipedia.org/wiki/Aadhaar,
               https://www.protecto.ai/blog/personal-dataset-sample-india-unique-identification-aadhaar-number-download-pii-data-examples

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    :param replacement_pairs: List of tuples with potential replacement values
    for different strings to be used during pattern matching.
    This can allow a greater variety in input, for example by removing dashes or spaces.
    """

    PATTERNS = [
        Pattern(
            "Aadhaar (high)",
            r"\b[1-9][0-9]{11}\b",
            0.8,
        ),

        Pattern(
            "Aadhaar (Medium)",
            r"\b[0-9]{12}\b",
            0.6,
        ),
        Pattern(
            "Aadhaar (Low)",
            r"\b[^0-9]*[0-9]{6}[^0-9]*\b",
            0.1,
        ),
    ]


    CONTEXT = [
        "Aadhaar card",
        "Aadhar card",
        "Aadhar",
        "Aadhaar",
        "UIDAI card",
        "unique identification card",
        "Aadhaar number",
    ]


    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "IN_AADHAAR",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
    ):
        self.replacement_pairs = (
            replacement_pairs if replacement_pairs else [("-", ""), (" ", "")]
        )
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
