"""Germany-specific recognizers."""

from .de_driver_license_recognizer import DeDriverLicenseRecognizer
from .de_id_card_recognizer import DeIdCardRecognizer
from .de_passport_recognizer import DePassportRecognizer
from .de_tax_id_recognizer import DeTaxIdRecognizer

__all__ = [
    "DeDriverLicenseRecognizer",
    "DeIdCardRecognizer",
    "DePassportRecognizer",
    "DeTaxIdRecognizer",
]
