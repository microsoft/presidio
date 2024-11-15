import logging
from abc import abstractmethod
from typing import Dict, List, Optional

from presidio_analyzer import RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

logger = logging.getLogger("presidio-analyzer")


class EntityRecognizer:
    """
    A class representing an abstract PII entity recognizer.

    EntityRecognizer is an abstract class to be inherited by
    Recognizers which hold the logic for recognizing specific PII entities.

    EntityRecognizer exposes a method called enhance_using_context which
    can be overridden in case a custom context aware enhancement is needed
    in derived class of a recognizer.

    :param supported_entities: the entities supported by this recognizer
    (for example, phone number, address, etc.)
    :param supported_language: the language supported by this recognizer.
    The supported langauge code is iso6391Name
    :param name: the name of this recognizer (optional)
    :param version: the recognizer current version
    :param context: a list of words which can help boost confidence score
    when they appear in context of the matched entity
    """

    MIN_SCORE = 0
    MAX_SCORE = 1.0

    def __init__(
        self,
        supported_entities: List[str],
        name: str = None,
        supported_language: str = "en",
        version: str = "0.0.1",
        context: Optional[List[str]] = None,
    ):
        self.supported_entities = supported_entities

        if name is None:
            self.name = self.__class__.__name__  # assign class name as name
        else:
            self.name = name

        self._id = f"{self.name}_{id(self)}"

        self.supported_language = supported_language
        self.version = version
        self.is_loaded = False
        self.context = context if context else []

        self.load()
        logger.info("Loaded recognizer: %s", self.name)
        self.is_loaded = True

    @property
    def id(self):
        """Return a unique identifier of this recognizer."""

        return self._id

    @abstractmethod
    def load(self) -> None:
        """
        Initialize the recognizer assets if needed.

        (e.g. machine learning models)
        """

    @abstractmethod
    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        """
        Analyze text to identify entities.

        :param text: The text to be analyzed
        :param entities: The list of entities this recognizer is able to detect
        :param nlp_artifacts: A group of attributes which are the result of
        an NLP process over the input text.
        :return: List of results detected by this recognizer.
        """
        return None

    def enhance_using_context(
        self,
        text: str,
        raw_recognizer_results: List[RecognizerResult],
        other_raw_recognizer_results: List[RecognizerResult],
        nlp_artifacts: NlpArtifacts,
        context: Optional[List[str]] = None,
    ) -> List[RecognizerResult]:
        """Enhance confidence score using context of the entity.

        Override this method in derived class in case a custom logic
        is needed, otherwise return value will be equal to
        raw_results.

        in case a result score is boosted, derived class need to update
        result.recognition_metadata[RecognizerResult.IS_SCORE_ENHANCED_BY_CONTEXT_KEY]

        :param text: The actual text that was analyzed
        :param raw_recognizer_results: This recognizer's results, to be updated
        based on recognizer specific context.
        :param other_raw_recognizer_results: Other recognizer results matched in
        the given text to allow related entity context enhancement
        :param nlp_artifacts: The nlp artifacts contains elements
                              such as lemmatized tokens for better
                              accuracy of the context enhancement process
        :param context: list of context words
        """
        return raw_recognizer_results

    def get_supported_entities(self) -> List[str]:
        """
        Return the list of entities this recognizer can identify.

        :return: A list of the supported entities by this recognizer
        """
        return self.supported_entities

    def get_supported_language(self) -> str:
        """
        Return the language this recognizer can support.

        :return: A list of the supported language by this recognizer
        """
        return self.supported_language

    def get_version(self) -> str:
        """
        Return the version of this recognizer.

        :return: The current version of this recognizer
        """
        return self.version

    def to_dict(self) -> Dict:
        """
        Serialize self to dictionary.

        :return: a dictionary
        """
        return_dict = {
            "supported_entities": self.supported_entities,
            "supported_language": self.supported_language,
            "name": self.name,
            "version": self.version,
        }
        return return_dict

    @classmethod
    def from_dict(cls, entity_recognizer_dict: Dict) -> "EntityRecognizer":
        """
        Create EntityRecognizer from a dict input.

        :param entity_recognizer_dict: Dict containing keys and values for instantiation
        """
        return cls(**entity_recognizer_dict)

    @staticmethod
    def remove_duplicates(results: List[RecognizerResult]) -> List[RecognizerResult]:
        """
        Remove duplicate results.

        Remove duplicates in case the two results
        have identical start and ends and types.
        :param results: List[RecognizerResult]
        :return: List[RecognizerResult]
        """
        results = list(set(results))
        results = sorted(results, key=lambda x: (-x.score, x.start, -(x.end - x.start)))
        filtered_results = []

        for result in results:
            if result.score == 0:
                continue

            to_keep = result not in filtered_results  # equals based comparison
            if to_keep:
                for filtered in filtered_results:
                    # If result is contained in one of the other results
                    if (
                        result.contained_in(filtered)
                        and result.entity_type == filtered.entity_type
                    ):
                        to_keep = False
                        break

            if to_keep:
                filtered_results.append(result)

        return filtered_results
