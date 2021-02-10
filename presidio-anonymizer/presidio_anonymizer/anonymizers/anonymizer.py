"""Anonymizers abstraction - each anonymizer should implement this class."""
import logging
from abc import abstractmethod, ABC


class Anonymizer(ABC):
    """Anonymizer abstract class to be implemented by each anonymizer."""

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
