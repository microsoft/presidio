import logging
import os
from abc import abstractmethod
import copy


class EntityRecognizer:
    MIN_SCORE = 0
    MAX_SCORE = 1.0
    CONTEXT_SIMILARITY_THRESHOLD = 0.65
    CONTEXT_SIMILARITY_FACTOR = 0.35
    MIN_SCORE_WITH_CONTEXT_SIMILARITY = 0.6
    CONTEXT_PREFIX_COUNT = 5
    CONTEXT_SUFFIX_COUNT = 0

    def __init__(self, supported_entities, name=None, supported_language="en",
                 version="0.0.1"):
        """
        An abstract class to be inherited by Recognizers which hold the logic
         for recognizing specific PII entities.
        :param supported_entities: the entities supported by this recognizer
        (for example, phone number, address, etc.)
        :param supported_language: the language supported by this recognizer.
        The supported langauge code is iso6391Name
        :param name: the name of this recognizer (optional)
        :param version: the recognizer current version
        """
        self.supported_entities = supported_entities

        if name is None:
            self.name = self.__class__.__name__  # assign class name as name
        else:
            self.name = name

        self.supported_language = supported_language
        self.version = version
        self.is_loaded = False

        loglevel = os.environ.get("LOG_LEVEL", "INFO")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)
        self.load()
        logging.info("Loaded recognizer: %s", self.name)
        self.is_loaded = True

    @abstractmethod
    def load(self):
        """
        Initialize the recognizer assets if needed
        (e.g. machine learning models)
        """

    @abstractmethod
    def analyze(self, text, entities, nlp_artifacts):
        """
        This is the core method for analyzing text, assuming entities are
        the subset of the supported entities types.

        :param text: The text to be analyzed
        :param entities: The list of entities to be detected
        :param nlp_artifacts: Value of type NlpArtifacts.
        A group of attributes which are the result of
                              some NLP process over the matching text
        :return: list of RecognizerResult
        :rtype: [RecognizerResult]
        """

        return None

    def get_supported_entities(self):
        """
        :return: A list of the supported entities by this recognizer
        """
        return self.supported_entities

    def get_supported_language(self):
        """
        :return: A list of the supported language by this recognizer
        """
        return self.supported_language

    def get_version(self):
        """
        :return: The current version of this recognizer
        """
        return self.version

    def to_dict(self):
        return_dict = {"supported_entities": self.supported_entities,
                       "supported_language": self.supported_language,
                       "name": self.name,
                       "version": self.version}
        return return_dict

    @classmethod
    def from_dict(cls, entity_recognizer_dict):
        return cls(**entity_recognizer_dict)

    def enhance_using_context(self, text, raw_results,
                              nlp_artifacts, predefined_context_words):
        """ using the surrounding words of the actual word matches, look
            for specific strings that if found contribute to the score
            of the result, improving the confidence that the match is
            indeed of that PII entity type

            :param text: The actual text that was analyzed
            :param raw_results: Recognizer results which didn't take
                                context into consideration
            :param nlp_artifacts: The nlp artifacts contains elements
                                  such as lemmatized tokens for better
                                  accuracy of the context enhancement process
            :param predefined_context_words: The words the current recognizer
                                             supports (words to lookup)
        """
        # create a deep copy of the results object so we can manipulate it
        results = copy.deepcopy(raw_results)

        # Sanity
        if nlp_artifacts is None:
            self.logger.warning('nlp artifacts were not provided')
            return results
        if predefined_context_words is None or predefined_context_words == []:
            self.logger.info('recognizer does not support context enhancement')
            return results

        for result in results:
            # extract lemmatized context from the surronding of the match
            self.logger.debug('match is \'%s\'', text[result.start:result.end])
            context = self.__extract_context(
                nlp_artifacts=nlp_artifacts,
                word=text[result.start:result.end],
                start=result.start)

            self.logger.debug('context is %s', context)
            context_similarity = self.__calculate_context_similarity(
                context, predefined_context_words)
            if context_similarity >= \
               self.CONTEXT_SIMILARITY_THRESHOLD:
                result.score += \
                  context_similarity * self.CONTEXT_SIMILARITY_FACTOR
                result.score = max(
                    result.score,
                    self.MIN_SCORE_WITH_CONTEXT_SIMILARITY)
                result.score = min(
                    result.score,
                    EntityRecognizer.MAX_SCORE)
        return results

    @staticmethod
    def __context_to_keywords(context):
        return context.split(' ')

    def __calculate_context_similarity(self,
                                       context_text,
                                       context_list):
        """Context similarity is 1 if there's exact match between a keyword in
           context_text and any keyword in context_list

        :param context_text a string of the prefix and suffix of the found
               match
        :param context_list a list of words considered as context keywords
        """

        if context_list is None:
            return 0

        context_keywords = self.__context_to_keywords(context_text)
        if context_keywords is None:
            return 0

        similarity = 0.0
        for context_keyword in context_keywords:
            if context_keyword in context_list:
                self.logger.info("Found context keyword '%s'", context_keyword)
                similarity = 1
                break

        return similarity

    def __extract_context(self, nlp_artifacts, word, start):
        """ Extracts words surronding another given word.
            The text from which the context is extracted is given in the nlp
            doc
            :param nlp_artifacts: An abstraction layer which holds different
                                  items which are result of a NLP pipeline
                                  execution on a given text
            :param word: The word to look for context around
            :param start: The start index of the word in the original text
        """

        if not nlp_artifacts.tokens:
            self.logger.info('Skipping context around \'%s\'', word)
            # if there are no nlp artifacts, this is ok, we can
            # extract context and we return a valid, yet empty
            # context
            return ''

        self.logger.debug('Extracting context around \'%s\'', word)
        context_keywords = nlp_artifacts.keywords

        found = False
        # we use the known start index of the original word to find the actual
        # token at that index, we are not checking for equivilance since the
        # token might be just a substring of that word (e.g. for phone number
        # 555-124564 the first token might be just '555')
        tokens = nlp_artifacts.tokens
        tokens_indices = nlp_artifacts.tokens_indices
        for i in range(len(nlp_artifacts.tokens)):
            if ((tokens_indices[i] == start) or
                    (tokens_indices[i] < start <
                     tokens_indices[i] + len(tokens[i]))):
                partial_token = tokens[i]
                found = True
                break

        token_count = 0
        if not found:
            raise ValueError("Did not find word '" + word + "' "
                             "in the list of tokens altough it "
                             "is expected to be found")

        # now, iterate over the lemmatized text to find the location of that
        # partial token
        for keyword in context_keywords:
            if keyword == partial_token:
                break
            token_count += 1

        # build the actual context
        context = ''
        i = 0
        for keyword in context_keywords:
            # if the current examined word is n chars before the token or m
            # after, add it to the context string
            if token_count - EntityRecognizer.CONTEXT_PREFIX_COUNT <= i + 1 \
                  <= token_count + EntityRecognizer.CONTEXT_SUFFIX_COUNT:
                context += ' ' + keyword
            i += 1

        self.logger.debug('Context sentence for word \'%s\' is: %s',
                          word,
                          context)
        return context
