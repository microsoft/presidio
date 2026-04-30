"""Ukraine-specific recognizers."""

from .ua_passport_recognizer import UaPassportRecognizer
from .ua_pension_id_recognizer import UaPensionIdRecognizer
from .ua_tax_id_recognizer import UaTaxIdRecognizer

__all__ = [
    "UaPassportRecognizer",
    "UaTaxIdRecognizer",
    "UaPensionIdRecognizer",
]
