from abc import ABC, abstractmethod


class NlpEngine(ABC):
    """ NlpEngine is an abstraction layer over the nlp module.
        It provides processing functionality as well as other queries
        on tokens
    """

    @abstractmethod
    def process_text(self, text, language):
        """ Execute the NLP pipeline on the given text and language
        """

    @abstractmethod
    def is_stopword(self, word, language):
        """ returns true if the given word is a stop word
            (within the given language)
        """

    @abstractmethod
    def is_punct(self, word, language):
        """ returns true if the given word is a punctuation word
            (within the given language)
        """
