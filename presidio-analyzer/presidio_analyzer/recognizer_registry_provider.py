import yaml
import os
import logging
from pathlib import Path
from typing import Optional, Union, List, Tuple, Dict, Any

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry, EntityRecognizer, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider, NlpEngine
import presidio_analyzer.recognizer_registry

logger = logging.getLogger("presidio-analyzer")


class RecognizerRegistryProvider:
    """
    Utility function for loading Presidio Analyzer.

    Use this class to load presidio analyzer engine from a yaml file
    """

    def __init__(self, conf_file: Optional[Union[Path, str]] = None, registry_configuration: Optional[Dict] = None,):
        self.configuration = {}

        if conf_file and registry_configuration:
            raise ValueError(
                "Either conf_file or registry_configuration should be provided, not both."
            )
        
        if registry_configuration:
            self.configuration = registry_configuration
            return

        if not conf_file or not os.path.exists(conf_file):
            logger.warning(
                "configuration file is missing. Using default configuration for recognizer registry engine"
            )
            return

        self.configuration = yaml.safe_load(open(conf_file))
        return

    def _is_recognizer_enabled(self, recognizer: Union[Dict[str, Any], str]) -> bool:
        return not "enabled" in recognizer or recognizer["enabled"]

    def _get_recognizer_name(self, recognizer: Union[Dict[str, Any], str]) -> str:
        if isinstance(recognizer, str):
            return recognizer
        return recognizer["name"]

    def _get_recognizer_items(self, recognizer: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        if isinstance(recognizer, str):
            return {}
        return recognizer.items()

    def _get_recognizer_languages(self, recognizer: Union[Dict[str, Any], str]) -> List[Dict[str, Any]]:
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

    def _create_custom_recognizers(self, recognizer: Dict) -> List[EntityRecognizer]:
        # in case supported_languages is not present, use the previous interface for custom recognizers
        if not "supported_languages" in recognizer:
            return [PatternRecognizer.from_dict(recognizer)]

        recognizers = []

        for supported_language in self._get_recognizer_languages(recognizer):
            copied_recognizer = {k: v for k, v in recognizer.items() if k not in ["enabled", "type", "supported_languages"]}
            recognizers.append(PatternRecognizer.from_dict({**copied_recognizer, **supported_language}))

        return recognizers

    def create_engine_recognizer_registry(self) -> RecognizerRegistry:
        recognizers=self.configuration.get("recognizers", [])
        recognizer_instances = []
        predefined, custom = self._split_recognizers(recognizers)
        for recognizer in predefined:
            for language in self._get_recognizer_languages(recognizer):
                if self._is_recognizer_enabled(recognizer):
                    copied_recognizer = {k: v for k, v in self._get_recognizer_items(recognizer) if k not in ["enabled", "type", "supported_languages", "name"]}
                    recognizer_instances.append(getattr(presidio_analyzer.predefined_recognizers, self._get_recognizer_name(recognizer), None)(**{**copied_recognizer, **language}))

        for recognizer in custom:
            if self._is_recognizer_enabled(recognizer):
                recognizer_instances.append(self._create_custom_recognizers(recognizer))

        global_regex_flags = self.configuration.get("global_regex_flags", None)
        for recognizer in recognizer_instances:
            recognizer.global_regex_flags = global_regex_flags

        return RecognizerRegistry(recognizers=recognizer_instances, global_regex_flags=global_regex_flags)