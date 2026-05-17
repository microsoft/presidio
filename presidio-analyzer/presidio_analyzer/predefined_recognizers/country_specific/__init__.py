"""Country-specific recognizers package."""

from .canada.ca_sin_recognizer import CaSinRecognizer
from .philippines.ph_license_plate_recognizer import PhLicensePlateRecognizer

__all__ = [
    "CaSinRecognizer",
    "PhLicensePlateRecognizer",
]
