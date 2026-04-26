"""Turkey-specific recognizers."""

from .tr_national_id_recognizer import TrNationalIdRecognizer
from .tr_phone_number_recognizer import TrPhoneNumberRecognizer

__all__ = [
    "TrNationalIdRecognizer",
    "TrPhoneNumberRecognizer",
]
