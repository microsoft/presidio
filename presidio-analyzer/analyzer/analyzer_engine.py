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
        # TODO: improve logic
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

    def Apply(self, request, context):
        logging.info("Starting Apply ")
        entities = self.__convert_fields_to_entities(
            request.analyzeTemplate.fields)
        language = self.__get_language(request.analyzeTemplate.fields)

        results = self.analyze(request.text, entities, language)

        # Create Analyze Response Object
        response = analyze_pb2.AnalyzeResponse()

        response.analyzeResults.extend(
            self.__convert_results_to_proto(results))
        logging.info("Found {} results".format(len(results)))
        return response

    def analyze(self, text, entities, language):
        """
        analyzes the requested text, searching for the given entities
         in the given language
        :param text: the text to analyze
        :param entities: the text to search
        :param language: the language of the text
        :return: an array of the found entities in the text
        """
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

    # TODO: These 3 methods below, should be removed as part of the work in:
    # user story #543 implement redesigned templates and
    # user story #8: Update APIs and Analyzer to direct specific
    # input language text to specific recognizers
    def __get_language(self, fields):
        # Currently each field hold its own language code
        # we are going to change it so we will get only one language
        # per request -> current logic: take the first language
        if not fields or len(fields) == 0 or fields[0].languageCode is None\
                or fields[0].languageCode == "":
            return DEFAULT_LANGUAGE

        return fields[0].languageCode

    def __convert_fields_to_entities(self, fields):
        # Convert fields to entities - will be changed once the API
        # will be changed
        entities = []
        for field in fields:
            entities.append(field.name)
        return entities

    def __convert_results_to_proto(self, results):
        proto_results = []
        for result in results:
            res = common_pb2.AnalyzeResult()
            res.field.name = result.entity_type
            res.score = result.score
            res.location.start = result.start
            res.location.end = result.end
            res.location.length = result.end - result.start
            proto_results.append(res)

        return proto_results
