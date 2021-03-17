from abc import ABC, abstractmethod


class EngineResultItem(ABC):
    """An abstract class to hold mutual data for engines results."""

    def __init__(self, start: int, end: int, entity_type: str):
        self.start = start
        self.end = end
        self.entity_type = entity_type

    @abstractmethod
    def __eq__(self, other):
        """Need to implement equal."""
        pass

    @abstractmethod
    def get_operated_text(self):
        """Need to implement for getting the text we operated on."""
        pass
