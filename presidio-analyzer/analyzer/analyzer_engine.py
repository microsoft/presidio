import logging
import os

import analyze_pb2
import analyze_pb2_grpc
import common_pb2

from analyzer import RecognizerRegistry
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

            # analyze using the current recognizer and append the results
            current_results = recognizer.analyze(text, entities, nlp_artifacts)
            if current_results:
                results.extend(current_results)

        return AnalyzerEngine.__remove_duplicates(results)

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
