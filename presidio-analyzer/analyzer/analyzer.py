import logging

import importlib
import grpc
import analyze_pb2
import analyze_pb2_grpc
from concurrent import futures
import time
import sys
import os
from google.protobuf.json_format import MessageToJson
from knack import CLI
from knack.arguments import ArgumentsContext
from knack.commands import CLICommandsLoader, CommandGroup
from knack.help import CLIHelp
from knack.help_files import helps

from analyzer import RecognizerRegistry

loglevel = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(message)s', level=loglevel)

DEFAULT_LANGUAGE = "en"


class Analyzer(analyze_pb2_grpc.AnalyzeServiceServicer):
    def __init__(self, registry=RecognizerRegistry()):
        # load all recognizers
        self.registry = registry
        registry.load_local_recognizer("predefined-recognizers")

    def __get_entities(self, requested_entities):
        """ If the requested entities array is empty,
            All the supported field types will be analyzed.
        """
        entities_list = []

        # get all supported entities from recognizers
        supported_entities = []
        for plugin in self.plugins:
            s = plugin.get_supported_entities()
            print(s)
            if isinstance(s, str):
                supported_entities.append(s)
            else:
                supported_entities.extend(s)

        print(supported_entities)

        if requested_entities is None or not requested_entities:
            entities_list = supported_entities
        else:
            for entity in requested_entities:
                entities_list.append(entity.name)

        return entities_list

    @staticmethod
    def __remove_duplicates(results):
        certain_results = list(filter(lambda r: r.score == 1.0, results))

        # Remove matches of the same text, if there's a match with score = 1
        filtered_results = []

        for result in results:
            valid_result = True
            if result not in certain_results:
                for certain_result in certain_results:
                    # If result is equal to or substring of a checksum result
                    if (result.text == certain_result.text
                            or (result.text in certain_result.text
                                and result.location.start >= certain_result.location.start
                                and result.location.end <= certain_result.location.end)):
                        valid_result = False
                        break

            if valid_result:
                filtered_results.append(result)

        return filtered_results

    def Apply(self, request, context):
        logging.info("Starting Apply " + request.text)

        response = analyze_pb2.AnalyzeResponse()
        entities = self.__get_entities(request.analyzeTemplate.fields)

        results = []

        recognizers = self.registry.get_recognizers(languages=[DEFAULT_LANGUAGE], entities=entities)
        for recognizer in recognizers:
            if not recognizer.is_loaded:
                recognizer.load()
                recognizer.is_loaded = True

            r = recognizer.analyze_text(request.text, entities)
            if r is not None:
                results.extend(r)

        results = Analyzer.__remove_duplicates(results)
        results.sort(key=lambda x: x.location.start, reverse=False)
        response.analyzeResults.extend(results)
        return response
