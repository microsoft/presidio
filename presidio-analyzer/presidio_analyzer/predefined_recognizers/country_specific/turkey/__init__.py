"""Turkey-specific recognizers."""

from .tr_license_plate_recognizer import TrLicensePlateRecognizer
from .tr_national_id_recognizer import TrNationalIdRecognizer
from .tr_phone_number_recognizer import TrPhoneNumberRecognizer

__all__ = [
    "TrLicensePlateRecognizer",
    "TrNationalIdRecognizer",
    "TrPhoneNumberRecognizer",
]
