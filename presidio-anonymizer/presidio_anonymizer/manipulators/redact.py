"""Replaces the PII text entity with empty string."""
from typing import Dict

from presidio_anonymizer.manipulators import Manipulator, ManipulatorType


class Redact(Manipulator):
    """Redact the string - empty value."""

    def manipulate(self, text: str = None, params: Dict = None) -> str:
        """:return: an empty value."""
        return ""

    def validate(self, params: Dict = None) -> None:
        """Redact does not require any paramters so no validation is needed."""
        pass

    def manipulator_name(self) -> str:
        """Return anonymizer name."""
        return "redact"

    def manipulator_type(self) -> ManipulatorType:
        """Return anonymizer name."""
        return ManipulatorType.Anonymize