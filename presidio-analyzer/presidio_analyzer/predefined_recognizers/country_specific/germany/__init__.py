"""Germany-specific recognizers."""

from .de_bsnr_recognizer import DeBsnrRecognizer
from .de_commercial_register_recognizer import DeCommercialRegisterRecognizer
from .de_driver_license_recognizer import DeDriverLicenseRecognizer
from .de_kvnr_recognizer import DeKvnrRecognizer
from .de_lanr_recognizer import DeLanrRecognizer
from .de_license_plate_recognizer import DeLicensePlateRecognizer
from .de_passport_recognizer import DePassportRecognizer
from .de_personal_id_recognizer import DePersonalIdRecognizer
from .de_postal_code_recognizer import DePostalCodeRecognizer
from .de_social_security_recognizer import DeSocialSecurityRecognizer
from .de_tax_id_recognizer import DeTaxIdRecognizer
from .de_telematik_id_recognizer import DeTelematikIdRecognizer
from .de_vat_code_recognizer import DeVatCodeRecognizer

__all__ = [
    "DeBsnrRecognizer",
    "DeCommercialRegisterRecognizer",
    "DeDriverLicenseRecognizer",
    "DeKvnrRecognizer",
    "DeLanrRecognizer",
    "DeLicensePlateRecognizer",
    "DePassportRecognizer",
    "DePersonalIdRecognizer",
    "DePostalCodeRecognizer",
    "DeSocialSecurityRecognizer",
    "DeTaxIdRecognizer",
    "DeTelematikIdRecognizer",
    "DeVatCodeRecognizer",
]
