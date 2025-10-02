"""Operator abstraction - each operator should implement this class."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict


class OperatorType(Enum):
    """Operator type either anonymize or decrypt to separate the operators."""

    Anonymize = 1
    Deanonymize = 2


types = [OperatorType.Anonymize, OperatorType.Deanonymize]


class Operator(ABC):
    """Operator abstract class to be implemented by each operator."""

    @abstractmethod
    def operate(self, text: str, params: Dict = None) -> str:
        """Operate method to be implemented in each operator."""
        pass

    @abstractmethod
    def validate(self, params: Dict = None) -> None:
        """Validate each operator parameters."""
        pass

    @abstractmethod
    def operator_name(self) -> str:
        """Return operator name."""
        pass

    @abstractmethod
    def operator_type(self) -> OperatorType:
        """Return operator type."""
        pass
