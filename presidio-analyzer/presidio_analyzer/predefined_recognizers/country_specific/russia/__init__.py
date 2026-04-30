"""Russia-specific recognizers."""

from .ru_inn_recognizer import RuInnRecognizer
from .ru_passport_recognizer import RuPassportRecognizer
from .ru_snils_recognizer import RuSnilsRecognizer

__all__ = [
    "RuPassportRecognizer",
    "RuInnRecognizer",
    "RuSnilsRecognizer",
]
