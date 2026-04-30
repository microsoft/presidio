"""Country-specific recognizers package."""

from .canada.ca_sin_recognizer import CaSinRecognizer
from .russia.ru_inn_recognizer import RuInnRecognizer
from .russia.ru_passport_recognizer import RuPassportRecognizer
from .russia.ru_snils_recognizer import RuSnilsRecognizer
from .ukraine.ua_passport_recognizer import UaPassportRecognizer
from .ukraine.ua_pension_id_recognizer import UaPensionIdRecognizer
from .ukraine.ua_tax_id_recognizer import UaTaxIdRecognizer

__all__ = [
    "CaSinRecognizer",
    "RuPassportRecognizer",
    "RuInnRecognizer",
    "RuSnilsRecognizer",
    "UaPassportRecognizer",
    "UaTaxIdRecognizer",
    "UaPensionIdRecognizer",
]
