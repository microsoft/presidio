"""Spain-specific recognizers package."""

from .es_nie_recognizer import EsNieRecognizer
from .es_nif_recognizer import EsNifRecognizer

__all__ = [
    "EsNifRecognizer",
    "EsNieRecognizer",
]
