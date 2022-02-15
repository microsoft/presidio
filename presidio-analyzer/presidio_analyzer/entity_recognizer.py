import logging
from abc import abstractmethod
from typing import List, Dict

from presidio_analyzer import RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

logger = logging.getLogger("presidio-analyzer")


class EntityRecognizer:
    """
    A class representing an abstract PII entity recognizer.

    EntityRecognizer is an abstract class to be inherited by
    Recognizers which hold the logic for recognizing specific PII entities.

    :param supported_entities: the entities supported by this recognizer
    (for example, phone number, address, etc.)
    :param supported_language: the language supported by this recognizer.
    The supported langauge code is iso6391Name
    :param name: the name of this recognizer (optional)
    :param version: the recognizer current version
    """

    MIN_SCORE = 0
    MAX_SCORE = 1.0

    context = []

    def __init__(
        self,
        supported_entities: List[str],
        name: str = None,
        supported_language: str = "en",
        version: str = "0.0.1",
    ):

        self.supported_entities = supported_entities

        if name is None:
            self.name = self.__class__.__name__  # assign class name as name
        else:
            self.name = name

        self.supported_language = supported_language
        self.version = version
        self.is_loaded = False

        self.load()
        logger.info("Loaded recognizer: %s", self.name)
        self.is_loaded = True

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
    def _find_index_of_match_token(
        word: str, start: int, tokens, tokens_indices: List[int]  # noqa ANN001
    ) -> int:
        found = False
        # we use the known start index of the original word to find the actual
        # token at that index, we are not checking for equivilance since the
        # token might be just a substring of that word (e.g. for phone number
        # 555-124564 the first token might be just '555' or for a match like '
        # rocket' the actual token will just be 'rocket' hence the misalignment
        # of indices)
        # Note: we are iterating over the original tokens (not the lemmatized)
        i = -1
        for i, token in enumerate(tokens, 0):
            # Either we found a token with the exact location, or
            # we take a token which its characters indices covers
            # the index we are looking for.
            if (tokens_indices[i] == start) or (start < tokens_indices[i] + len(token)):
                # found the interesting token, the one that around it
                # we take n words, we save the matching lemma
                found = True
                break

        if not found:
            raise ValueError(
                "Did not find word '" + word + "' "
                "in the list of tokens although it "
                "is expected to be found"
            )
        return i

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
