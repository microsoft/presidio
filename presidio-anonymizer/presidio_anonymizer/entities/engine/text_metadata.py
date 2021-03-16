from abc import abstractmethod, ABC


class TextMetadata(ABC):
    def __gt__(self, other):
        return self.end > other.end

    def __eq__(self, other):
        return self.start == other.start \
               and self.end == other.end \
               and self.entity_type == other.entity_type

    @abstractmethod
    def get_start(self) -> int:
        pass

    @abstractmethod
    def get_end(self) -> int:
        pass

    @abstractmethod
    def get_entity_type(self) -> str:
        pass