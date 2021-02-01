from abc import ABC, abstractmethod

from presidio_analyzer.nlp_engine import NlpArtifacts


class NlpEngine(ABC):
    """
    NlpEngine is an abstraction layer over the nlp module.

    It provides NLP preprocessing functionality as well as other queries
    on tokens.
    """

    @abstractmethod
    def process_text(self, text: str, language: str) -> NlpArtifacts:
        """Execute the NLP pipeline on the given text and language."""

    @abstractmethod
    def is_stopword(self, word: str, language: str) -> bool:
        """
        Return true if the given word is a stop word.

        (within the given language)
        """

    @abstractmethod
    def is_punct(self, word: str, language: str) -> bool:
        """
        Return true if the given word is a punctuation word.

        (within the given language)
        """
