"""Keeps the PII text unmodified."""

from abc import ABC
from typing import Dict

from presidio_anonymizer.operators import Operator, OperatorType


class BaseKeep(Operator, ABC):
    """Abstract base class for keep operators.

    Implements the common functionality of keep operators, leaving the operator
    type to be implemented by concrete classes
    """

    def operate(self, text: str = None, params: Dict = None) -> str:
        """:return: original text."""
        return text

    def validate(self, params: Dict = None) -> None:
        """Keep does not require any parameters so no validation is needed."""
        pass


class Keep(BaseKeep):
    """No-op anonymizer that keeps the PII text unmodified.

    This is useful when you don't want to anonymize some types of PII,
    but wants to keep track of it with the other PIIs.
    """

    def operator_name(self) -> str:
        """Return operator name."""
        return "keep"

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Anonymize
