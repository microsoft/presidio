from abc import ABC, abstractmethod


class EngineResultItem(ABC):

    @abstractmethod
    def __eq__(self, other):
        pass

