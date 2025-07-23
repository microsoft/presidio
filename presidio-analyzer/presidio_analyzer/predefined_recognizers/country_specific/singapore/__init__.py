"""Singapore-specific recognizers package."""

from .sg_uen_recognizer import SgUenRecognizer
from .sg_fin_recognizer import SgFinRecognizer

__all__ = [
    "SgUenRecognizer",
    "SgFinRecognizer",
]
