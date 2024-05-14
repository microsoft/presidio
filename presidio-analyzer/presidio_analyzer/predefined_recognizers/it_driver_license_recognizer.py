from typing import List, Optional

from presidio_analyzer import Pattern, PatternRecognizer


class ItDriverLicenseRecognizer(PatternRecognizer):
    """
    Recognizes IT Driver License using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """

    PATTERNS = [
        Pattern(
            "Driver License",
            (
                r"\b(?i)(([A-Z]{2}\d{7}[A-Z])"
                r"|(^[U]1[BCDEFGHLMNPRSTUWYXZ]\w{6}[A-Z]))\b"
            ),
            0.2,
        ),
    ]
    CONTEXT = [
        "driverlic",
        "driverlics",
        "driverlicense",
        "driverlicenses",
        "driverlicence",
        "driverlicences",
        "driver lic",
        "driver lics",
        "driver license",
        "driver licenses",
        "driver licence",
        "driver licences",
        "driverslic",
        "driverslics",
        "driverslicence",
        "driverslicences",
        "driverslicense",
        "driverslicenses",
        "drivers lic",
        "drivers lics",
        "drivers license",
        "drivers licenses",
        "drivers licence",
        "drivers licences",
        "driver'lic",
        "driver'lics",
        "driver'license",
        "driver'licenses",
        "driver'licence",
        "driver'licences",
        "driver' lic",
        "driver' lics",
        "driver' license",
        "driver' licenses",
        "driver' licence",
        "driver' licences",
        "driver'slic",
        "driver'slics",
        "driver'slicense",
        "driver'slicenses",
        "driver'slicence",
        "driver'slicences",
        "driver's lic",
        "driver's lics",
        "driver's license",
        "driver's licenses",
        "driver's licence",
        "driver's licences",
        "dl#",
        "dls#",
        "driverlic#",
        "driverlics#",
        "driverlicense#",
        "driverlicenses#",
        "driverlicence#",
        "driverlicences#",
        "driver lic#",
        "driver lics#",
        "driver license#",
        "driver licenses#",
        
        "patente", "patente di guida", "licenza", "licenza di guida"]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "it",
        supported_entity: str = "IT_DRIVER_LICENSE",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            patterns=patterns,
            context=context,
            supported_language=supported_language,
        )
