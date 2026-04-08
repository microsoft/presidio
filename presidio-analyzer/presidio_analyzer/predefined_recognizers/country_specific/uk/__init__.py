"""UK-specific recognizers package."""

from .uk_nhs_recognizer import NhsRecognizer
from .uk_nino_recognizer import UkNinoRecognizer
from .uk_passport_recognizer import UkPassportRecognizer
from .uk_postcode_recognizer import UkPostcodeRecognizer
from .uk_vehicle_registration_recognizer import UkVehicleRegistrationRecognizer

__all__ = [
    "NhsRecognizer",
    "UkNinoRecognizer",
    "UkPassportRecognizer",
    "UkPostcodeRecognizer",
    "UkVehicleRegistrationRecognizer",
]
