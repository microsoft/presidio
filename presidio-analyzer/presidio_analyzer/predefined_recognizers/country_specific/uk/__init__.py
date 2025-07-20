"""UK-specific recognizers package."""

from .uk_nhs_recognizer import NhsRecognizer
from .uk_nino_recognizer import UkNinoRecognizer

__all__ = [
    "NhsRecognizer",
    "UkNinoRecognizer",
]
