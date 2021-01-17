from abc import abstractmethod, ABC

"""
Anonymizers abstraction
"""


class Anonymizer(ABC):
    """Anonymizer abstract class to be implemented by each anonymizer."""

    @abstractmethod
    def anonymize(self):
        """Anonymize method to be implemented in each anonymizer."""
        pass
