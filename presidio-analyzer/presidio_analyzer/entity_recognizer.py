import copy
from abc import abstractmethod

from presidio_analyzer import PresidioLogger


class EntityRecognizer:
    MIN_SCORE = 0
    MAX_SCORE = 1.0
    CONTEXT_SIMILARITY_THRESHOLD = 0.65
    CONTEXT_SIMILARITY_FACTOR = 0.35
    MIN_SCORE_WITH_CONTEXT_SIMILARITY = 0.4
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

        self.logger = PresidioLogger()
        self.load()
        self.logger.info("Loaded recognizer: %s", self.name)
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
                              nlp_artifacts, recognizer_context_words):
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
            :param recognizer_context_words: The words the current recognizer
                                             supports (words to lookup)
        """
        # create a deep copy of the results object so we can manipulate it
        results = copy.deepcopy(raw_results)

        # Sanity
        if nlp_artifacts is None:
            self.logger.warning('[%s]. NLP artifacts were not provided',
                                self.name)
            return results
        if recognizer_context_words is None or recognizer_context_words == []:
            self.logger.info("recognizer '%s' does not support context "
                             "enhancement", self.name)
            return results

        for result in results:
            # extract lemmatized context from the surrounding of the match

            word = text[result.start:result.end]

            surrounding_words = self.__extract_surrounding_words(
                nlp_artifacts=nlp_artifacts,
                word=word,
                start=result.start)

            supportive_context_word = self.__find_supportive_word_in_context(
                surrounding_words, recognizer_context_words)
            if supportive_context_word != "":
                result.score += \
                  self.CONTEXT_SIMILARITY_FACTOR
                result.score = max(
                    result.score,
                    self.MIN_SCORE_WITH_CONTEXT_SIMILARITY)
                result.score = min(
                    result.score,
                    EntityRecognizer.MAX_SCORE)

                # Update the explainability object with context information
                # helped improving the score
                result.analysis_explanation.set_supportive_context_word(
                    supportive_context_word)
                result.analysis_explanation.set_improved_score(result.score)
        return results

    @staticmethod
    def __context_to_keywords(context):
        return context.split(' ')

    def __find_supportive_word_in_context(self,
                                          context_list,
                                          recognizer_context_list):
        """A word is considered a supportive context word if
           there's exact match between a keyword in
           context_text and any keyword in context_list

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
            result = \
              next((True for keyword in context_list
                    if predefined_context_word in keyword), False)
            if result:
                self.logger.debug("Found context keyword '%s'",
                                  predefined_context_word)
                word = predefined_context_word
                break

        return word

    @staticmethod
    def __add_n_words(index,
                      n_words,
                      lemmas,
                      lemmatized_filtered_keywords,
                      is_backward):
        """ Prepare a string of context words, which surrounds a lemma
            at a given index. The words will be collected only if exist
            in the filtered array

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
            i = i-1 if is_backward else i+1
        return context_words

    def __add_n_words_forward(self,
                              index,
                              n_words,
                              lemmas,
                              lemmatized_filtered_keywords):
        return self.__add_n_words(
            index,
            n_words,
            lemmas,
            lemmatized_filtered_keywords,
            False)

    def __add_n_words_backward(self,
                               index,
                               n_words,
                               lemmas,
                               lemmatized_filtered_keywords):
        return self. __add_n_words(
            index,
            n_words,
            lemmas,
            lemmatized_filtered_keywords,
            True)

    @staticmethod
    def find_index_of_match_token(word, start, tokens, tokens_indices):
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
            if ((tokens_indices[i] == start) or
                    (start < tokens_indices[i] + len(token))):
                # found the interesting token, the one that around it
                # we take n words, we save the matching lemma
                found = True
                break

        if not found:
            raise ValueError("Did not find word '" + word + "' "
                             "in the list of tokens although it "
                             "is expected to be found")
        return i

    def __extract_surrounding_words(self, nlp_artifacts, word, start):
        """ Extracts words surrounding another given word.
            The text from which the context is extracted is given in the nlp
            doc
            :param nlp_artifacts: An abstraction layer which holds different
                                  items which are the result of a NLP pipeline
                                  execution on a given text
            :param word: The word to look for context around
            :param start: The start index of the word in the original text
        """

        if not nlp_artifacts.tokens:
            self.logger.info('Skipping context extraction due to '
                             'lack of NLP artifacts')
            # if there are no nlp artifacts, this is ok, we can
            # extract context and we return a valid, yet empty
            # context
            return ''

        # Get the already prepared words in the given text, in their
        # LEMMATIZED version
        lemmatized_keywords = nlp_artifacts.keywords

        # since the list of tokens is not necessarily aligned
        # with the actual index of the match, we look for the
        # token index which corresponds to the match
        token_index = EntityRecognizer.find_index_of_match_token(
            word,
            start,
            nlp_artifacts.tokens,
            nlp_artifacts.tokens_indices)

        # index i belongs to the PII entity, take the preceding n words
        # and the successing m words into a context list

        backward_context = \
            self.__add_n_words_backward(token_index,
                                        EntityRecognizer.CONTEXT_PREFIX_COUNT,
                                        nlp_artifacts.lemmas,
                                        lemmatized_keywords)
        forward_context = \
            self.__add_n_words_forward(token_index,
                                       EntityRecognizer.CONTEXT_SUFFIX_COUNT,
                                       nlp_artifacts.lemmas,
                                       lemmatized_keywords)

        context_list = []
        context_list.extend(backward_context)
        context_list.extend(forward_context)
        context_list = list(set(context_list))
        self.logger.debug('Context list is: %s', " ".join(context_list))
        return context_list
