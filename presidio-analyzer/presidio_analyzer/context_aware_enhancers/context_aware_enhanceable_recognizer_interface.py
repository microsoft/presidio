import abc
from typing import List, Optional

from presidio_analyzer import RecognizerResult, EntityRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts


class ContextAwareEnhanceableRecognizerInterface(metaclass=abc.ABCMeta):
    """
    When a recognizer needs implement a custom context aware enhancement
    logic it should inherit from this interface and implement the abstract
    method.
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'enhance_using_context') and
                callable(subclass.enhance_using_context) or
                NotImplemented)

    @abc.abstractmethod
    def enhance_using_context(
            self,
            text: str,
            raw_results: List[RecognizerResult],
            nlp_artifacts: NlpArtifacts,
            recognizers: List[EntityRecognizer],
            context: Optional[List[str]] = None,
    ) -> List[RecognizerResult]:
        """
        Implement this method in concrete recognizer to update result
        in case a custom logic is needed.

        :param text: The actual text that was analyzed
        :param raw_results: Recognizer results which didn't take
                            context into consideration
        :param nlp_artifacts: The nlp artifacts contains elements
                              such as lemmatized tokens for better
                              accuracy of the context enhancement process
        :param recognizers: the list of recognizers
        :param context: list of context words
        """
        raise NotImplementedError
