"""Spain-specific recognizers package."""

from .es_nie_recognizer import EsNieRecognizer
from .es_nif_recognizer import EsNifRecognizer
from .es_passport_recognizer import EsPassportRecognizer

__all__ = [
    "EsNifRecognizer",
    "EsNieRecognizer",
    "EsPassportRecognizer",
]
