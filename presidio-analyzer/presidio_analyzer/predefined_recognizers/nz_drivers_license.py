from presidio_analyzer import Pattern, PatternRecognizer
from typing import Optional, List, Tuple

class NZDriversLicenseNumber(PatternRecognizer):
    """
    Recognizes Indian UIDAI Person Identification Number ("AADHAAR").

    Reference: https://en.wikipedia.org/wiki/Aadhaar
    A 12 digit unique number that is issued to each individual by Government of India
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
            "NZDriversLicenseNumber (Medium)",
            r"\b[A-Z]{2}\d{6}\b",
            0.4,
        ),
    ]

    CONTEXT = [
        "driverlicence",
        "driverlicences",
        "driver lic",
        "driver licence",
        "driver licences",
        "driverslic",
        "driverslicence",
        "driverslicences",
        "drivers lic",
        "drivers lics",
        "drivers licence",
        "drivers licences",
        "driver'lic",
        "driver'lics",
        "driver'licence",
        "driver'licences",
        "driver' lic",
        "driver' lics",
        "driver' licence",
        "driver' licences",
        "driver'slic",
        "driver'slics",
        "driver'slicence",
        "driver'slicences",
        "driver's lic",
        "driver's lics",
        "driver's licence",
        "driver's licences",
        "driverlic#",
        "driverlics#",
        "driverlicence#",
        "driverlicences#",
        "driver lic#",
        "driver lics#",
        "driver licence#",
        "driver licences#",
        "driverslic#",
        "driverslics#",
        "driverslicence#",
        "driverslicences#",
        "drivers lic#",
        "drivers lics#",
        "drivers licence#",
        "drivers licences#",
        "driver'lic#",
        "driver'lics#",
        "driver'licence#",
        "driver'licences#",
        "driver' lic#",
        "driver' lics#",
        "driver' licence#",
        "driver' licences#",
        "driver'slic#",
        "driver'slics#",
        "driver'slicence#",
        "driver'slicences#",
        "driver's lic#",
        "driver's lics#",
        "driver's licence#",
        "driver's licences#",
        "international driving permit",
        "international driving permits",
        "nz automobile association",
        "new zealand automobile association"
    ]

    utils = None

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "NZ_DRIVERS_LICENSE",
        replacement_pairs: Optional[List[Tuple[str, str]]] = None,
    ):
        
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )

        # custom attributes
        self.type = 'alphanumeric'
        self.range = (8,8)