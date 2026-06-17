"""Country-specific recognizers package."""

from .canada.ca_sin_recognizer import CaSinRecognizer
from .philippines.ph_philhealth_recognizer import PhPhilhealthRecognizer

__all__ = [
    "CaSinRecognizer",
    "PhPhilhealthRecognizer",
]
