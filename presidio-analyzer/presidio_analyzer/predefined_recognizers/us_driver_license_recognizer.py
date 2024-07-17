from typing import Optional, List

from presidio_analyzer import Pattern, PatternRecognizer

# List from https://ntsi.com/drivers-license-format/
# ---------------

# WA Driver License number is relatively unique as it also
# includes '*' chars.
# However it can also be 12 letters which makes every 12 letter'
# word a match. Therefore we split WA driver license
# regex: r'\b([A-Z][A-Z0-9*]{11})\b' into two regexes
# With different weights, one to indicate letters only and
# one to indicate at least one digit or one '*'


class UsLicenseRecognizer(PatternRecognizer):
    """
    Recognizes US driver license using regex.

    :param patterns: List of patterns to be used by this recognizer
    :param context: List of context words to increase confidence in detection
    :param supported_language: Language this recognizer supports
    :param supported_entity: The entity this recognizer can detect
    """
    #TODO - include 50 states individual regexes
    PATTERNS = [
        Pattern(
            "Driver License - Alphanumeric (weak)",
            r"([A-Z][0-9]{3,6}|[A-Z][0-9]{5,9}|[A-Z][0-9]{6,8}|[A-Z][0-9]{4,8}|[A-Z][0-9]{9,11}|[A-Z]{1,2}[0-9]{5,6}|H[0-9]{8}|V[0-9]{6}|X[0-9]{8}|A-Z]{2}[0-9]{2,5}|[A-Z]{2}[0-9]{3,7}|[0-9]{2}[A-Z]{3}[0-9]{5,6}|[A-Z][0-9]{13,14}|[A-Z][0-9]{18}|[A-Z][0-9]{6}R|[A-Z][0-9]{9}|[A-Z][0-9]{1,12}|[0-9]{9}[A-Z]|[A-Z]{2}[0-9]{6}[A-Z]|[0-9]{8}[A-Z]{2}|[0-9]{3}[A-Z]{2}[0-9]{4}|[A-Z][0-9][A-Z][0-9][A-Z]|[0-9]{7,8}[A-Z])",  # noqa: E501
            0.3,
        ),
    ]

    CONTEXT = [
        "DL",
        "DLS",
        "CDL",
        "CDLS",
        "ID",
        "IDs",
        "DL#",
        "DLS#",
        "CDL#",
        "CDLS#",
        "ID#",
        "IDs#",
        "ID number",
        "ID numbers",
        "DLN",

        "driver",
        "license",
        "permit",
        "lic",
        "identification",
        "dls",
        "cdls",
        "lic#",
        "driving",

        "DriverLic",
        "DriverLics",
        "DriverLicense",
        "DriverLicenses",
        "Driver Lic",
        "Driver Lics",
        "Driver License",
        "Driver Licenses",
        "DriversLic",
        "DriversLics",
        "DriversLicense",
        "DriversLicenses",
        "Drivers Lic",
        "Drivers Lics",
        "Drivers License",
        "Drivers Licenses",
        "Driver'Lic",
        "Driver'Lics",
        "Driver'License",
        "Driver'Licenses",
        "Driver' Lic",
        "Driver' Lics",
        "Driver' License",
        "Driver' Licenses",
        "Driver'sLic",
        "Driver'sLics",
        "Driver'sLicense",
        "Driver'sLicenses",
        "Driver's Lic",
        "Driver's Lics",
        "Driver's License",
        "Driver's Licenses",
        "identification number",
        "identification numbers",
        "identification #",
        "id card",
        "id cards",
        "identification card",
    ]

    def __init__(
        self,
        patterns: Optional[List[Pattern]] = None,
        context: Optional[List[str]] = None,
        supported_language: str = "en",
        supported_entity: str = "US_DRIVER_LICENSE",
    ):
        patterns = patterns if patterns else self.PATTERNS
        context = context if context else self.CONTEXT
        super().__init__(
            supported_entity=supported_entity,
            supported_language=supported_language,
            patterns=patterns,
            context=context,
        )

        # custom attributes
        self.type = 'numeric/alphanumeric'
        self.range = (7,14)
