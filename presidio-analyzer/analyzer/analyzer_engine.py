import logging
import analyze_pb2
import analyze_pb2_grpc
import common_pb2
import os

from analyzer import RecognizerRegistry
from analyzer import ContextEnhancer

loglevel = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(message)s', level=loglevel)

DEFAULT_LANGUAGE = "en"


class AnalyzerEngine(analyze_pb2_grpc.AnalyzeServiceServicer):
    def __init__(self, registry=RecognizerRegistry()):
        # load all recognizers
        self.registry = registry
        self.context_enhancer = ContextEnhancer()
        registry.load_local_recognizer("predefined-recognizers")

    @staticmethod
    def __remove_duplicates(results):

        filtered_results = []

        for result in results:
            valid_result = True
            if result not in filtered_results:
                for filtered in filtered_results:
                    # If result is equal to or substring of a checksum result
                    if result.start >= filtered.start and result.end <= filtered.end:
                        valid_result = False
                        break

            if valid_result:
                filtered_results.append(result)

        return filtered_results

    def Apply(self, request, context):
        logging.info("Starting Apply " + request.text)
        entities = self.__convert_fields_to_entities(request.analyzeTemplate.fields)
        results = self.analyze(request.text, entities)

        # enhance results with context
        for result in results:
            result = self.context_enhancer.enhance_score()

        response = analyze_pb2.AnalyzeResponse()        
        response.analyzeResults.extend(self.__convert_results_to_proto(results))
        logging.info("Found " + len(results) + " results")
        return response

    def analyze(self, text, entities):
        recognizers = self.registry.get_recognizers(languages=[DEFAULT_LANGUAGE], entities=entities)
        results = []

        for recognizer in recognizers:
            # Lazy load of the relevant recognizers
            if not recognizer.is_loaded:
                recognizer.load()
                recognizer.is_loaded = True

            r = recognizer.analyze_all(text, entities)
            if r is not None:
                results.extend(r)

        sorted(results, key=lambda x: (x.start, x.score))
        return AnalyzerEngine.__remove_duplicates(results)

    def __convert_fields_to_entities(self, fields):
        # Convert fields to entities - will be changed once the API will be changed
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
