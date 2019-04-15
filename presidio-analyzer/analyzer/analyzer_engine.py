import copy
import logging
import os

import analyze_pb2
import analyze_pb2_grpc
import common_pb2

from analyzer import RecognizerRegistry, PatternRecognizer, \
    EntityRecognizer
from analyzer.nlp_engine import SpacyNlpEngine

loglevel = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(message)s', level=loglevel)

DEFAULT_LANGUAGE = "en"


class AnalyzerEngine(analyze_pb2_grpc.AnalyzeServiceServicer):

    def __init__(self, registry=RecognizerRegistry(),
                 nlp_engine=SpacyNlpEngine()):
        # load nlp module
        self.nlp_engine = nlp_engine
        # prepare registry
        self.registry = registry
        # load all recognizers
        registry.load_predefined_recognizers()

    # pylint: disable=unused-argument
    def Apply(self, request, context):
        logging.info("Starting Apply")
        entities = AnalyzerEngine.__convert_fields_to_entities(
            request.analyzeTemplate.fields)
        language = AnalyzerEngine.get_language_from_request(request)
        results = self.analyze(request.text, entities, language,
                               request.analyzeTemplate.allFields)

        # Create Analyze Response Object
        response = analyze_pb2.AnalyzeResponse()

        # pylint: disable=no-member
        response.analyzeResults.extend(
            AnalyzerEngine.__convert_results_to_proto(results))
        logging.info("Found %d results", len(results))
        return response

    @staticmethod
    def __remove_duplicates(results):
        # bug# 597: Analyzer remove duplicates doesn't handle all cases of one
        # result as a substring of the other
        results = sorted(results,
                         key=lambda x: (-x.score, x.start, x.end - x.start))
        filtered_results = []

        for result in results:
            if result.score == 0:
                continue

            valid_result = True
            if result not in filtered_results:
                for filtered in filtered_results:
                    # If result is equal to or substring of
                    # one of the other results
                    if result.start >= filtered.start \
                          and result.end <= filtered.end:
                        valid_result = False
                        break

            if valid_result:
                filtered_results.append(result)

        return filtered_results

    @classmethod
    def get_language_from_request(cls, request):
        language = request.analyzeTemplate.language
        if language is None or language == "":
            language = DEFAULT_LANGUAGE
        return language

    def analyze(self, text, entities, language, all_fields):
        """
        analyzes the requested text, searching for the given entities
         in the given language
        :param text: the text to analyze
        :param entities: the text to search
        :param language: the language of the text
        :param all_fields: a Flag to return all fields
        of the requested language
        :return: an array of the found entities in the text
        """

        recognizers = self.registry.get_recognizers(language=language,
                                                    entities=entities,
                                                    all_fields=all_fields)

        if all_fields:
            if entities:
                raise ValueError("Cannot have both all_fields=True "
                                 "and a populated list of entities. "
                                 "Either have all_fields set to True "
                                 "and entities are empty, or all_fields "
                                 "is False and entities is populated")
            # Since all_fields=True, list all entities by iterating
            # over all recognizers
            entities = self.__list_entities(recognizers)

        # run the nlp pipeline over the given text, store the results in
        # a NlpArtifacts instance
        nlp_artifacts = self.nlp_engine.process_text(text, language)
        results = []
        for recognizer in recognizers:
            # Lazy loading of the relevant recognizers
            if not recognizer.is_loaded:
                recognizer.load()
                recognizer.is_loaded = True

            raw_results = recognizer.analyze(text, entities, nlp_artifacts)
            if raw_results is not None:
                # try to improve the results score using the surronding context
                # words
                raw_results = \
                    self.enhance_using_context(
                        text, recognizer, raw_results, nlp_artifacts)
                results.extend(raw_results)

        return AnalyzerEngine.__remove_duplicates(results)

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
                logging.info("Found context keyword '%s'", context_keyword)
                similarity = 1
                break

        return similarity

    def enhance_using_context(self, text, recognizer, raw_results,
                              nlp_artifacts):
        # create a deep copy of the results object so we can manipulate it
        results = copy.deepcopy(raw_results)

        # Sanity
        if nlp_artifacts is None:
            logging.warning('nlp artifacts were not provided')
            return results
        if not hasattr(recognizer, 'context'):
            logging.info('recognizer does not support context enhancement')
            return results

        for result in results:
            # extract lemmatized context from the surronding of the match
            logging.debug('match is \'%s\'', text[result.start:result.end])
            context = self.__extract_context(
                nlp_artifacts=nlp_artifacts,
                word=text[result.start:result.end],
                start=result.start)

            logging.debug('context is %s', context)
            context_similarity = self.__calculate_context_similarity(
                context, recognizer.context)
            if context_similarity >= \
               PatternRecognizer.CONTEXT_SIMILARITY_THRESHOLD:
                result.score += \
                  context_similarity * \
                  PatternRecognizer.CONTEXT_SIMILARITY_FACTOR
                result.score = max(
                    result.score,
                    PatternRecognizer.MIN_SCORE_WITH_CONTEXT_SIMILARITY)
                result.score = min(
                    result.score,
                    EntityRecognizer.MAX_SCORE)
        return results

    @staticmethod
    def __context_to_keywords(context):
        return context.split(' ')

    @staticmethod
    def __extract_context(nlp_artifacts, word, start):
        """ Extracts words surronding another given word.
            The text from which the context is extracted is given in the nlp
            doc
            :param nlp_artifacts: An abstraction layer which holds different
                                  items which are result of a NLP pipeline
                                  execution on a given text
            :param word: The word to look for context around
            :param start: The start index of the word in the original text
        """

        logging.debug('Extracting context around \'%s\'', word)
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
                partial_token = tokens_indices[i]
                found = True
                break

            # no need to continue iterating after the word is found
            if found:
                break

        token_count = 0
        if not found:
            logging.error('Did not find expected word: %s', word)
            return ''

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
            if token_count - PatternRecognizer.CONTEXT_PREFIX_COUNT <= i + 1 \
                  <= token_count + PatternRecognizer.CONTEXT_SUFFIX_COUNT:
                context += ' ' + keyword
            i += 1

        logging.debug('Context sentence for word \'%s\' is: %s',
                      word,
                      context)
        return context

    @staticmethod
    def __list_entities(recognizers):
        entities = []
        for recognizer in recognizers:
            ents = [entity for entity in recognizer.supported_entities]
            entities.extend(ents)

        return list(set(entities))

    @staticmethod
    def __convert_fields_to_entities(fields):
        # Convert fields to entities - will be changed once the API
        # will be changed
        entities = []
        for field in fields:
            entities.append(field.name)
        return entities

    @staticmethod
    def __convert_results_to_proto(results):
        proto_results = []
        for result in results:
            res = common_pb2.AnalyzeResult()
            # pylint: disable=no-member
            res.field.name = result.entity_type
            res.score = result.score
            # pylint: disable=no-member
            res.location.start = result.start
            res.location.end = result.end
            res.location.length = result.end - result.start
            proto_results.append(res)

        return proto_results
