import copy
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
    CONTEXT_SIMILARITY_THRESHOLD = 0.65
    CONTEXT_SIMILARITY_FACTOR = 0.35
    MIN_SCORE_WITH_CONTEXT_SIMILARITY = 0.4
    CONTEXT_PREFIX_COUNT = 5
    CONTEXT_SUFFIX_COUNT = 0

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

    def enhance_using_context(
        self,
        text: str,
        raw_results: List[RecognizerResult],
        nlp_artifacts: NlpArtifacts,
        recognizer_context_words: List[str],
    ) -> List[RecognizerResult]:
        """
        Update results in case surrounding words are relevant to the context words.

        Using the surrounding words of the actual word matches, look
        for specific strings that if found contribute to the score
        of the result, improving the confidence that the match is
        indeed of that PII entity type

        :param text: The actual text that was analyzed
        :param raw_results: Recognizer results which didn't take
                            context into consideration
        :param nlp_artifacts: The nlp artifacts contains elements
                              such as lemmatized tokens for better
                              accuracy of the context enhancement process
        :param recognizer_context_words: The words the current recognizer
                                         supports (words to lookup)
        """
        # create a deep copy of the results object so we can manipulate it
        results = copy.deepcopy(raw_results)

        # Sanity
        if nlp_artifacts is None:
            logger.warning("[%s]. NLP artifacts were not provided", self.name)
            return results
        if recognizer_context_words is None or recognizer_context_words == []:
            logger.info(
                "recognizer '%s' does not support context " "enhancement", self.name
            )
            return results

        for result in results:
            # extract lemmatized context from the surrounding of the match

            word = text[result.start : result.end]

            surrounding_words = self.__extract_surrounding_words(
                nlp_artifacts=nlp_artifacts, word=word, start=result.start
            )

            supportive_context_word = self.__find_supportive_word_in_context(
                surrounding_words, recognizer_context_words
            )
            if supportive_context_word != "":
                result.score += self.CONTEXT_SIMILARITY_FACTOR
                result.score = max(result.score, self.MIN_SCORE_WITH_CONTEXT_SIMILARITY)
                result.score = min(result.score, EntityRecognizer.MAX_SCORE)

                # Update the explainability object with context information
                # helped improving the score
                result.analysis_explanation.set_supportive_context_word(
                    supportive_context_word
                )
                result.analysis_explanation.set_improved_score(result.score)
        return results

    @staticmethod
    def __context_to_keywords(context: str) -> List[str]:
        return context.split(" ")

    @staticmethod
    def __find_supportive_word_in_context(
        context_list: List[str], recognizer_context_list: List[str]
    ) -> str:
        """
        Find words in the text which are relevant for context evaluation.

        A word is considered a supportive context word if there's exact match
        between a keyword in context_text and any keyword in context_list.

        :param context_list words before and after the matched entity within
               a specified window size
        :param recognizer_context_list a list of words considered as
                context keywords manually specified by the recognizer's author
        """
        word = ""
        # If the context list is empty, no need to continue
        if context_list is None or recognizer_context_list is None:
            return word

        for predefined_context_word in recognizer_context_list:
            # result == true only if any of the predefined context words
            # is found exactly or as a substring in any of the collected
            # context words
            result = next(
                (
                    True
                    for keyword in context_list
                    if predefined_context_word in keyword
                ),
                False,
            )
            if result:
                logger.debug("Found context keyword '%s'", predefined_context_word)
                word = predefined_context_word
                break

        return word

    @staticmethod
    def __add_n_words(
        index: int,
        n_words: int,
        lemmas: List[str],
        lemmatized_filtered_keywords: List[str],
        is_backward: bool,
    ) -> List[str]:
        """
        Prepare a string of context words.

        Return a list of words which surrounds a lemma at a given index.
        The words will be collected only if exist in the filtered array

        :param index: index of the lemma that its surrounding words we want
        :param n_words: number of words to take
        :param lemmas: array of lemmas
        :param lemmatized_filtered_keywords: the array of filtered
               lemmas from the original sentence,
        :param is_backward: if true take the preceeding words, if false,
                            take the successing words
        """
        i = index
        context_words = []
        # The entity itself is no interest to us...however we want to
        # consider it anyway for cases were it is attached with no spaces
        # to an interesting context word, so we allow it and add 1 to
        # the number of collected words

        # collect at most n words (in lower case)
        remaining = n_words + 1
        while 0 <= i < len(lemmas) and remaining > 0:
            lower_lemma = lemmas[i].lower()
            if lower_lemma in lemmatized_filtered_keywords:
                context_words.append(lower_lemma)
                remaining -= 1
            i = i - 1 if is_backward else i + 1
        return context_words

    def __add_n_words_forward(
        self,
        index: int,
        n_words: int,
        lemmas: List[str],
        lemmatized_filtered_keywords: List[str],
    ) -> List[str]:
        return self.__add_n_words(
            index, n_words, lemmas, lemmatized_filtered_keywords, False
        )

    def __add_n_words_backward(
        self,
        index: int,
        n_words: int,
        lemmas: List[str],
        lemmatized_filtered_keywords: List[str],
    ) -> List[str]:
        return self.__add_n_words(
            index, n_words, lemmas, lemmatized_filtered_keywords, True
        )

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

    def __extract_surrounding_words(
        self, nlp_artifacts: NlpArtifacts, word: str, start: int
    ) -> List[str]:
        """Extract words surrounding another given word.

        The text from which the context is extracted is given in the nlp
        doc.

        :param nlp_artifacts: An abstraction layer which holds different
                              items which are the result of a NLP pipeline
                              execution on a given text
        :param word: The word to look for context around
        :param start: The start index of the word in the original text
        """
        if not nlp_artifacts.tokens:
            logger.info("Skipping context extraction due to " "lack of NLP artifacts")
            # if there are no nlp artifacts, this is ok, we can
            # extract context and we return a valid, yet empty
            # context
            return [""]

        # Get the already prepared words in the given text, in their
        # LEMMATIZED version
        lemmatized_keywords = nlp_artifacts.keywords

        # since the list of tokens is not necessarily aligned
        # with the actual index of the match, we look for the
        # token index which corresponds to the match
        token_index = EntityRecognizer._find_index_of_match_token(
            word, start, nlp_artifacts.tokens, nlp_artifacts.tokens_indices
        )

        # index i belongs to the PII entity, take the preceding n words
        # and the successing m words into a context list

        backward_context = self.__add_n_words_backward(
            token_index,
            EntityRecognizer.CONTEXT_PREFIX_COUNT,
            nlp_artifacts.lemmas,
            lemmatized_keywords,
        )
        forward_context = self.__add_n_words_forward(
            token_index,
            EntityRecognizer.CONTEXT_SUFFIX_COUNT,
            nlp_artifacts.lemmas,
            lemmatized_keywords,
        )

        context_list = []
        context_list.extend(backward_context)
        context_list.extend(forward_context)
        context_list = list(set(context_list))
        logger.debug("Context list is: %s", " ".join(context_list))
        return context_list

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
        results = sorted(results, key=lambda x: (-x.score, x.start, x.end - x.start))
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
