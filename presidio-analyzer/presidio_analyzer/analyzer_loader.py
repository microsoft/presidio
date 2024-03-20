import yaml
import os
import logging
from typing import List

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider
import presidio_analyzer.recognizer_registry

logger = logging.getLogger("presidio-analyzer")


class PresidioAnalyzerLoader:
    """
    Utility function for loading Presidio Analyzer.

    Use this class to load presidio analyzer engine from a yaml file
    """

    @staticmethod
    def load(conf_file: str) -> AnalyzerEngine:
        """
        loads Presidio Analyzer from yaml configuration file.

        :param conf_file: yaml file containing definitions
        :return: analyzer engine initialized with yaml configuration
        """

        if not os.path.exists(conf_file):
            return AnalyzerEngine()

        logger.info("loading static engine")
        configuration = yaml.safe_load(open(conf_file))

        nlp_engine = None
        supported_languages = None
        registry = None

        if "nlp_configuration" in configuration and "nlp_engine_provider" in configuration["nlp_engine_provider"]:
            nlp_configuration = configuration["nlp_engine_provider"]["nlp_configuration"]
            provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
            nlp_engine = provider.create_engine()

        if "supported_languages" in configuration:
            supported_languages = configuration["supported_languages"]

        if "recognizer_registry" in configuration and "recognizers" in configuration["recognizer_registry"]:
            recognizers = configuration["recognizer_registry"]["recognizers"]
            recognizer_instances = [getattr(presidio_analyzer.predefined_recognizers, PresidioAnalyzerLoader._get_name(recognizer), None)(supported_language=language) 
                                        for recognizer in recognizers
                                        for language in PresidioAnalyzerLoader._get_languages(recognizer)]
            registry = RecognizerRegistry(recognizers=recognizer_instances)

        analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine, 
            supported_languages=supported_languages,
            registry=registry
        )

        return analyzer

    @staticmethod
    def _get_name(recognizer: str) ->str :
        if isinstance(recognizer, str):
            return recognizer
        return recognizer["name"]

    @staticmethod
    def _get_languages(recognizer: str) -> List[str]:
        if isinstance(recognizer, str):
            return ["en"]
        return recognizer["supported_language"]