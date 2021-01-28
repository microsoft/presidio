"""Anonymizers abstraction - each anonymizer should implement this class."""
import logging
from abc import abstractmethod, ABC


class Anonymizer(ABC):
    """Anonymizer abstract class to be implemented by each anonymizer."""

    logger = logging.getLogger("presidio-anonymizer")

    @abstractmethod
    def anonymize(self, original_text, params):
        """Anonymize method to be implemented in each anonymizer."""
        pass
