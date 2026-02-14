"""UK-specific recognizers package."""

from .uk_driving_licence_recognizer import UkDrivingLicenceRecognizer
from .uk_nhs_recognizer import NhsRecognizer
from .uk_nino_recognizer import UkNinoRecognizer

__all__ = [
    "NhsRecognizer",
    "UkDrivingLicenceRecognizer",
    "UkNinoRecognizer",
]
