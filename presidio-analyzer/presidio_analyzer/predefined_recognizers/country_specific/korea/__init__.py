"""Korea-specific recognizers."""

from .kr_passport_recognizer import KrPassportRecognizer
from .kr_rrn_recognizer import KrRrnRecognizer

__all__ = [
    "KrRrnRecognizer",
    "KrPassportRecognizer",
]
