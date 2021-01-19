"""Anonymizers abstraction - each anonymizer should implement this class."""
from abc import abstractmethod, ABC


class Anonymizer(ABC):
    """Anonymizer abstract class to be implemented by each anonymizer."""

    @abstractmethod
    def anonymize(self):
        """Anonymize method to be implemented in each anonymizer."""
        pass
