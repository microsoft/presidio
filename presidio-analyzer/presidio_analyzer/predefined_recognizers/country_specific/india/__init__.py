"""India-specific recognizers."""

from .in_aadhaar_recognizer import InAadhaarRecognizer
from .in_pan_recognizer import InPanRecognizer
from .in_passport_recognizer import InPassportRecognizer
from .in_vehicle_recognizer import InVehicleRecognizer
from .in_voter_recognizer import InVoterRecognizer

__all__ = [
    "InAadhaarRecognizer",
    "InPanRecognizer",
    "InVoterRecognizer",
    "InVehicleRecognizer",
    "InPassportRecognizer",
]
