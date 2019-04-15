from abc import ABC, abstractmethod


class NlpEngine(ABC):
    """ NlpEngine is an abstraction layer over the nlp module.
        It provides processing functionality as well as other queries
        on tokens
    """

    @abstractmethod
    def process_text(self, text, language):
        pass

    @abstractmethod
    def is_stopword(self, word, language):
        pass
