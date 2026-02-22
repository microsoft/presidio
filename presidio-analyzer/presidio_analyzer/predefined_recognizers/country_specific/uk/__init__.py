"""UK-specific recognizers package."""

from .uk_driving_licence_recognizer import UkDrivingLicenceRecognizer
from .uk_nhs_recognizer import NhsRecognizer
from .uk_nino_recognizer import UkNinoRecognizer
from .uk_postcode_recognizer import UkPostcodeRecognizer

__all__ = [
    "NhsRecognizer",
    "UkDrivingLicenceRecognizer",
    "UkNinoRecognizer",
    "UkPostcodeRecognizer",
]
