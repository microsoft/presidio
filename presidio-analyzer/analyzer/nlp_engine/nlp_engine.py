from abc import ABC, abstractmethod


class NlpEngine(ABC):

    @abstractmethod
    def process_text(self, text, language):
        pass

    @abstractmethod
    def is_stopword(self, word, language):
        pass
