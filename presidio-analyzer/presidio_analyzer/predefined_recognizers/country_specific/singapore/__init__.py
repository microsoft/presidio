"""Singapore-specific recognizers package."""

from .sg_fin_recognizer import SgFinRecognizer
from .sg_uen_recognizer import SgUenRecognizer

__all__ = [
    "SgUenRecognizer",
    "SgFinRecognizer",
]
