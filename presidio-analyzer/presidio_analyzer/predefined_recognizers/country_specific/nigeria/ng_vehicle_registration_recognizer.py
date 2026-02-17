from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class NgVehicleRegistrationRecognizer(PatternRecognizer):
    """
    Recognizes Nigerian vehicle registration plate numbers (current format, 2011+).

    The current format is: ABC-123DE
    - 3 letters: LGA (Local Government Area) code
    - Hyphen separator (may be omitted or replaced with space)
    - 3 digits: serial number (001-999)
    - 2 letters: year code + batch code

    Reference: https://en.wikipedia.org/wiki/Vehicle_registration_plates_of_Nigeria

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Nigeria Vehicle Registration",
            r"\b[A-Z]{3}[- ]?\d{3}[A-Z]{2}\b",
            0.5,
        ),
    ]

    CONTEXT = [
        "plate number",
        "vehicle registration",
        "license plate",
        "number plate",
        "plate",
        "vehicle",
        "registration",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "NG_VEHICLE_REGISTRATION",
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
