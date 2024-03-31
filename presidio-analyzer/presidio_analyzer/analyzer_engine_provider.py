import yaml
import os
import logging
from pathlib import Path
from typing import Optional, Union, List, Tuple, Dict, Any

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry, EntityRecognizer, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider, NlpEngine
import presidio_analyzer.recognizer_registry

logger = logging.getLogger("presidio-analyzer")


class AnalyzerEngineProvider:
    """
    Utility function for loading Presidio Analyzer.

    Use this class to load presidio analyzer engine from a yaml file
    """

    def __init__(self, conf_file: Optional[Union[Path, str]] = None):
        self.configuration = {}
        if not conf_file or not os.path.exists(conf_file):
            logger.warning(
                "configuration file is missing. Using default configuration for analyzer engine"
            )
            return
        
        self.configuration = yaml.safe_load(open(conf_file))
        return


    def create_engine(self) -> AnalyzerEngine:
        """
        loads Presidio Analyzer from yaml configuration file.

        :return: analyzer engine initialized with yaml configuration
        """

        nlp_engine = self._load_nlp_engine()
        registry = self._load_recognizer_registry()
        supported_languages = "en"
        default_score_threshold = 0
        if "analyzer_engine" not in self.configuration:
            logger.warning(
                "configuration file is missing 'analyzer_engine'. Using default configuration for analyzer engine"
                )
        else:
            supported_languages = self.configuration.get("supported_languages", "en")
            default_score_threshold = self.configuration.get("default_score_threshold", 0)

        analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine, 
            registry=registry,
            supported_languages=supported_languages,
            default_score_threshold=default_score_threshold
        )

        return analyzer
    
    def _is_enabled(self, recognizer: Union[Dict[str, Any], str]) -> bool:
        return not "enabled" in recognizer or recognizer["enabled"]

    def _get_name(self, recognizer: Union[Dict[str, Any], str]) -> str:
        if isinstance(recognizer, str):
            return recognizer
        return recognizer["name"]

    def _get_items(self, recognizer: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        if isinstance(recognizer, str):
            return {}
        return recognizer.items()

    def _get_languages(self, recognizer: Union[Dict[str, Any], str]) -> List[Dict[str, Any]]:
        if isinstance(recognizer, str) or "supported_languages" not in recognizer:
            logger.warning("language was not specified, defaulting to English")
            return [{"supported_language": "en", "context": None}]
        if isinstance(recognizer["supported_languages"][0], str):
            return [{"supported_language": language, "context": None} for language in recognizer["supported_languages"]]
        return [{"supported_language": language["language"], "context": language["context"]} for language in recognizer["supported_languages"]]

    def _split_recognizers(self, recognizers: Union[Dict[str, Any], str]) -> Tuple[List[Dict[str, Any]],List[Dict[str, Any]]]:
        """
        splits the recognizer list to predefined and custom
        """
        predefined =[]
        custom =[]

        predefined = [recognizer for recognizer in recognizers if isinstance(recognizer, str) or ("type" in recognizer and recognizer["type"] == "predefined")]
        # all recognizers are custom by default, type: custom can be mentioned as well
        custom = [recognizer for recognizer in recognizers if not isinstance(recognizer, str) and ("type" not in recognizer or recognizer["type"] == "custom")]
        return predefined, custom

    def _create_recognizers(self, recognizer: Dict) -> List[EntityRecognizer]:
        # in case supported_languages is not present, use the previous interface for custom recognizers
        if not "supported_languages" in recognizer:
            return [PatternRecognizer.from_dict(recognizer)]

        recognizers = []

        for supported_language in self._get_languages(recognizer):
            copied_recognizer = {k: v for k, v in recognizer.items() if k not in ["enabled", "type", "supported_languages"]}
            recognizers.append(PatternRecognizer.from_dict({**copied_recognizer, **supported_language}))

        return recognizers

    def _load_recognizer_registry(self) -> RecognizerRegistry:
        if "recognizer_registry" not in self.configuration:
            logger.warning(
                "configuration file is missing 'recognizer_registry'. Using default configuration for recognizer registry"
            )
            return None
        recognizer_registry = self.configuration["recognizer_registry"]
        if isinstance(recognizer_registry, str):
            if recognizer_registry!="predefined":
                logger.warning(
                "recognizer_registry contains unidentified value. Using default configuration for recognizer registry"
                )
            return None

        recognizers=recognizer_registry["recognizers"]
        recognizer_instances = []
        predefined, custom = self._split_recognizers(recognizers)
        for recognizer in predefined:
            for language in self._get_languages(recognizer):
                if self._is_enabled(recognizer):
                    copied_recognizer = {k: v for k, v in self._get_items(recognizer) if k not in ["enabled", "type", "supported_languages", "name"]}
                    recognizer_instances.append(getattr(presidio_analyzer.predefined_recognizers, self._get_name(recognizer), None)(**{**copied_recognizer, **language}))

        for recognizer in custom:
            if self._is_enabled(recognizer):
                recognizer_instances.append(self._create_recognizers(recognizer))

        global_regex_flags = recognizer_registry.get("global_regex_flags", None)

        return RecognizerRegistry(recognizers=recognizer_instances, global_regex_flags=global_regex_flags)
    
    def _load_nlp_engine(self) -> NlpEngine:
        if "nlp_configuration" not in self.configuration:
            logger.warning(
                "configuration file is missing 'nlp_configuration'. Using default configuration for nlp engine"
            )
            return None
        nlp_configuration = self.configuration["nlp_configuration"]
        provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
        return provider.create_engine()