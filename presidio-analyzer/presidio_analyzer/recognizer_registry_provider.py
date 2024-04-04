import yaml
import os
import logging
from pathlib import Path
from typing import Optional, Union, List, Tuple, Dict, Any

from presidio_analyzer import RecognizerRegistry, EntityRecognizer, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider, NlpEngine
import presidio_analyzer.recognizer_registry

logger = logging.getLogger("presidio-analyzer")


class RecognizerRegistryProvider:
    """
    Utility class for loading Recognizer Registry.

    Use this class to load recognzer registry from a yaml file
    """

    def __init__(self, conf_file: Optional[Union[Path, str]] = None, registry_configuration: Optional[Dict] = None, supported_languages: List[str] = None):
        if conf_file and registry_configuration:
            raise ValueError(
                "Either conf_file or registry_configuration should be provided, not both."
            )
        
        self.configuration = self._get_configuration(conf_file, registry_configuration)

        if not supported_languages:
            supported_languages = ["en"]
        self.supported_languages = self.configuration.get("supported_languages", supported_languages)
        return
    
    def _get_configuration(self, conf_file: Union[Path, str], registry_configuration: Dict) -> Union[Dict[str, Any]]:
        if registry_configuration:
            return registry_configuration

        if not conf_file or not os.path.exists(conf_file):
            logger.warning(
                "configuration file is missing. Using default configuration for recognizer registry engine"
            )
            conf_file = self._get_full_conf_path()

        return yaml.safe_load(open(conf_file))

    def _is_recognizer_enabled(self, recognizer: Union[Dict[str, Any], str]) -> bool:
        return not "enabled" in recognizer or recognizer["enabled"]

    def _get_recognizer_name(self, recognizer: Union[Dict[str, Any], str]) -> str:
        if isinstance(recognizer, str):
            return recognizer
        return recognizer["name"]

    def _get_recognizer_context(self, recognizer: Union[Dict[str, Any], str]) -> List[str]:
        if isinstance(recognizer, str):
            return None
        return recognizer["context"]

    def _get_recognizer_items(self, recognizer: Union[Dict[str, Any], str]) -> Dict[str, Any]:
        if isinstance(recognizer, str):
            return {}
        return recognizer.items()

    def _get_recognizer_languages(self, recognizer: Union[Dict[str, Any], str]) -> List[Dict[str, Any]]:
        """
        Gets the different language properties for each recognizer. Creating a new recognizer for each supported language. 
        If language wasn't specified, create a recognizer for each supported language.

        :param recognizer: The afordmentioned recognizer.
        :return: The list of recognizers in the supported languages. 
        """
        if isinstance(recognizer, str) or "supported_languages" not in recognizer:
            return [{"supported_language": language, "context": self._get_recognizer_context(recognizer)} for language in self.supported_languages]
        if isinstance(recognizer["supported_languages"][0], str):
            return [{"supported_language": language, "context": None} for language in recognizer["supported_languages"]]
        return [{"supported_language": language["language"], "context": language["context"]} for language in recognizer["supported_languages"]]

    def _split_recognizers(self, recognizers: Union[Dict[str, Any], str]) -> Tuple[List[Dict[str, Any]],List[Dict[str, Any]]]:
        """
        splits the recognizer list to predefined and custom. All recognizers are predefined by default though type: 'predefined' can be mentioned as well
        """
        predefined =[]
        custom =[]

        predefined = [recognizer for recognizer in recognizers if isinstance(recognizer, str) or ("type" in recognizer and recognizer["type"] == "predefined")]
        # 
        custom = [recognizer for recognizer in recognizers if not isinstance(recognizer, str) and ("type" not in recognizer or recognizer["type"] == "custom")]
        return predefined, custom

    def _create_custom_recognizers(self, recognizer: Dict) -> List[EntityRecognizer]:
        recognizers = []

        for supported_language in self._get_recognizer_languages(recognizer):
            copied_recognizer = {k: v for k, v in recognizer.items() if k not in ["enabled", "type", "supported_languages"]}
            recognizers.append(PatternRecognizer.from_dict({**copied_recognizer, **supported_language}))

        return recognizers

    def create_recognizer_registry(self) -> RecognizerRegistry:
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
            if isinstance(recognizer, PatternRecognizer):
                recognizer.global_regex_flags = global_regex_flags

        return RecognizerRegistry(recognizers=recognizer_instances, global_regex_flags=global_regex_flags)

    @staticmethod
    def _get_full_conf_path(
        default_conf_file: Union[Path, str] = "default_recognizers.yaml"
    ) -> Path:
        """Return a Path to the default conf file."""
        return Path(Path(__file__).parent.parent, "conf", default_conf_file)