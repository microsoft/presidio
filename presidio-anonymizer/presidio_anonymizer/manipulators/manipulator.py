"""Manipulator abstraction - each manipulator should implement this class."""
import logging
from abc import abstractmethod, ABC
from enum import Enum
from typing import Dict


class ManipulatorType(Enum):
    Anonymize = 1
    Decrypt = 2


class Manipulator(ABC):
    """Manipulator abstract class to be implemented by each manipulator."""

    _anonymizers: Dict = None
    _decryptors: Dict = None

    logger = logging.getLogger("presidio-anonymizer")

    @abstractmethod
    def manipulate(self, text: str, params: Dict = None) -> str:
        """Anonymize method to be implemented in each manipulator."""
        pass

    @abstractmethod
    def validate(self, params: Dict = None) -> None:
        """Validate each manipulator parameters."""
        pass

    @abstractmethod
    def manipulator_name(self) -> str:
        """Return manipulator name."""
        pass

    @abstractmethod
    def manipulator_type(self) -> ManipulatorType:
        """Return manipulator type."""
        pass

    @staticmethod
    def get_anonymizers() -> \
            Dict[str, "Manipulator"]:
        """Return all anonymizers classes currently available."""
        if not Manipulator._anonymizers:
            Manipulator._anonymizers = Manipulator.__get_manipulators_by_type(
                ManipulatorType.Anonymize)
        return Manipulator._anonymizers

    @staticmethod
    def get_decryptors() -> \
            Dict[str, "Manipulator"]:
        """Return all anonymizers classes currently available."""
        if not Manipulator._decryptors:
            Manipulator._decryptors = Manipulator.__get_manipulators_by_type(
                ManipulatorType.Decrypt)
        return Manipulator._decryptors

    @staticmethod
    def __get_manipulators_by_type(manipulator_type: ManipulatorType):
        manipulators = Manipulator.__subclasses__()
        manipulators = list(filter(
            lambda cls: cls.manipulator_type(cls) == manipulator_type,
            manipulators))
        return {
            cls.manipulator_name(cls): cls for
            cls in manipulators
        }
