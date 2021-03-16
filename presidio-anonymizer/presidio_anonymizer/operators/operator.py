"""Operator abstraction - each operator should implement this class."""
import logging
from abc import abstractmethod, ABC
from enum import Enum
from typing import Dict


class OperatorType(Enum):
    Anonymize = 1
    Decrypt = 2


class Operator(ABC):
    """Operator abstract class to be implemented by each operator."""

    _anonymizers: Dict = None
    _decryptors: Dict = None

    logger = logging.getLogger("presidio-anonymizer")

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

    @staticmethod
    def get_anonymizers() -> \
            Dict[str, "Operator"]:
        """Return all anonymizers classes currently available."""
        if not Operator._anonymizers:
            Operator._anonymizers = Operator.__get_operators_by_type(
                OperatorType.Anonymize)
        return Operator._anonymizers

    @staticmethod
    def get_decryptors() -> \
            Dict[str, "Operator"]:
        """Return all decryptors classes currently available."""
        if not Operator._decryptors:
            Operator._decryptors = Operator.__get_operators_by_type(
                OperatorType.Decrypt)
        return Operator._decryptors

    @staticmethod
    def __get_operators_by_type(manipulator_type: OperatorType):
        manipulators = Operator.__subclasses__()
        manipulators = list(filter(
            lambda cls: cls.operator_type(cls) == manipulator_type,
            manipulators))
        return {
            cls.operator_name(cls): cls for
            cls in manipulators
        }
