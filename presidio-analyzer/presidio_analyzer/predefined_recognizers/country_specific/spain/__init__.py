"""Spain-specific recognizers package."""

from .es_nif_recognizer import EsNifRecognizer
from .es_nie_recognizer import EsNieRecognizer

__all__ = [
    "EsNifRecognizer",
    "EsNieRecognizer",
]
