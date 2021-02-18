"""Anonymizers abstraction - each anonymizer should implement this class."""
import logging
from abc import abstractmethod, ABC
from typing import List


class Anonymizer(ABC):
    """Anonymizer abstract class to be implemented by each anonymizer."""

    _anonymizers = None

    logger = logging.getLogger("presidio-anonymizer")

    @abstractmethod
    def anonymize(self, text: str, params: dict = None) -> str:
        """Anonymize method to be implemented in each anonymizer."""
        pass

    @abstractmethod
    def validate(self, params: dict = None) -> None:
        """Validate each anonymizer parameters."""
        pass

    @abstractmethod
    def anonymizer_name(self) -> str:
        """Return anonymizer name."""
        pass

    @staticmethod
    def get_anonymizers() -> List[str]:
        """Return all anonymizers classes currently available."""
        if not Anonymizer._anonymizers:
            Anonymizer._anonymizers = {
                cls.anonymizer_name(cls): cls
                for cls in Anonymizer.__subclasses__()
            }
        return Anonymizer._anonymizers
