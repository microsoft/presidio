"""Anonymizers abstraction - each anonymizer should implement this class."""
import logging
from abc import abstractmethod, ABC
from typing import Dict


class Anonymizer(ABC):
    """Anonymizer abstract class to be implemented by each anonymizer."""

    _anonymizers: Dict = None

    logger = logging.getLogger("presidio-anonymizer")

    @abstractmethod
    def anonymize(self, text: str, params: Dict = None) -> str:
        """Anonymize method to be implemented in each anonymizer."""
        pass

    @abstractmethod
    def validate(self, params: Dict = None) -> None:
        """Validate each anonymizer parameters."""
        pass

    @abstractmethod
    def anonymizer_name(self) -> str:
        """Return anonymizer name."""
        pass

    @staticmethod
    def get_anonymizers() -> Dict[str, 'Anonymizer']:
        """Return all anonymizers classes currently available."""
        if not Anonymizer._anonymizers:
            Anonymizer._anonymizers = {
                cls.anonymizer_name(cls): cls
                for cls in Anonymizer.__subclasses__()
            }
        return Anonymizer._anonymizers
