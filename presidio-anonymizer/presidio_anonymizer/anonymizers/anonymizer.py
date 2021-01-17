from abc import abstractmethod, ABC


class Anonymizer(ABC):
    @abstractmethod
    def anonymize(self):
        pass
