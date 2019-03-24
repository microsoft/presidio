import logging
import os

import analyze_pb2
import analyze_pb2_grpc
import common_pb2

from analyzer import RecognizerRegistry  # noqa: F401

loglevel = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(message)s', level=loglevel)

DEFAULT_LANGUAGE = "en"


class AnalyzerEngine(analyze_pb2_grpc.AnalyzeServiceServicer):

    def __init__(self, registry=RecognizerRegistry()):
        # load all recognizers
        self.registry = registry
        registry.load_recognizers("predefined-recognizers")

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

    # pylint: disable=unused-argument
    def Apply(self, request, context):
        logging.info("Starting Apply")
        entities = AnalyzerEngine.__convert_fields_to_entities(
            request.analyzeTemplate.fields)
        language = AnalyzerEngine.get_language_from_request(request)
        results = self.analyze(request.text, entities, language, request.analyzeTemplate.allFields)

        # Create Analyze Response Object
        response = analyze_pb2.AnalyzeResponse()

        # pylint: disable=no-member
        response.analyzeResults.extend(
            AnalyzerEngine.__convert_results_to_proto(results))
        logging.info("Found %d results", len(results))
        return response

    @classmethod
    def get_language_from_request(request):
        language = request.analyzeTemplate.language
        if language is None or language == "":
            language = DEFAULT_LANGUAGE
        return language

    def analyze(self, text, entities, language, all_fields=False):
        """
        analyzes the requested text, searching for the given entities
         in the given language
        :param text: the text to analyze
        :param entities: the text to search
        :param language: the language of the text
        :param all_fields: a Flag to return all fields of the requested language
        :return: an array of the found entities in the text
        """
        if all_fields:
            recognizers = self.registry.get_all_recognizers_by_language(language=language)
        else:
            recognizers = self.registry.get_recognizers(language=language,
                                                        entities=entities)
        results = []

        for recognizer in recognizers:
            # Lazy loading of the relevant recognizers
            if not recognizer.is_loaded:
                recognizer.load()
                recognizer.is_loaded = True

            r = recognizer.analyze(text, entities)
            if r is not None:
                results.extend(r)

        return AnalyzerEngine.__remove_duplicates(results)

    def add_pattern_recognizer(self, pattern_recognizer_dict):
        """
        Adds a new recognizer
        :param pattern_recognizer_dict: a dictionary representation
         of a pattern recognizer
        """
        self.registry.add_pattern_recognizer_from_dict(pattern_recognizer_dict)

    def remove_recognizer(self, name):
        """
        Removes an existing recognizer, throws an exception if not found
        :param name: name of recognizer to be removed
        """
        self.registry.remove_recognizer(name)

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
