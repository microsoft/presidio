from abc import ABC, abstractmethod


class EngineResultItem(ABC):
    def __init__(self, start: int, end: int, entity_type: str):
        self.start = start
        self.end = end
        self.entity_type = entity_type

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def get_operated_text(self):
        pass
