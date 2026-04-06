"""Sweden-specific recognizers."""

from .se_organisationsnummer_recognizer import SeOrganisationsnummerRecognizer
from .se_personnummer_recognizer import SePersonnummerRecognizer

__all__ = [
    "SeOrganisationsnummerRecognizer",
    "SePersonnummerRecognizer",
]
