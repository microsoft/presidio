from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class DeDriverLicenseRecognizer(PatternRecognizer):
    """
    Recognizes German driver license numbers (Fuhrerscheinnummer).

    The German driver license number is an 11-character alphanumeric
    string with the pattern: one alphanumeric character, two digits,
    six alphanumeric characters, one digit, and one alphanumeric character.

    Reference: https://en.wikipedia.org/wiki/European_driving_licence

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Driver License (very weak)",
            r"\b[A-Z0-9]\d{2}[A-Z0-9]{6}\d[A-Z0-9]\b",
            0.01,
        ),
    ]

    CONTEXT = [
        "fuhrerschein",
        "fuhrerscheinnummer",
        "fahrerlaubnis",
        "driver license",
        "driving licence",
        "fahrerlaubnisnummer",
        "fuhrerscheinklasse",
        "strassenverkehrsamt",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "de",
        supported_entity: str = "DE_DRIVER_LICENSE",
        name: Optional[str] = None,
    ) -> None:
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
            name=name,
        )
