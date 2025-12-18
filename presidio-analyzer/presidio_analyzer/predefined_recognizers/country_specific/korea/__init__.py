"""Korea-specific recognizers."""

from .kr_rrn_recognizer import KrRrnRecognizer
from .kr_driver_license_recognizer import KrDriverLicenseRecognizer

__all__ = [
    "KrRrnRecognizer",
    "KrDriverLicenseRecognizer",
]
