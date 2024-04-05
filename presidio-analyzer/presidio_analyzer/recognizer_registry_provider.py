import re
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

    def __init__(self, conf_file: Optional[Union[Path, str]] = None, registry_configuration: Optional[Dict] = None):
        self.configuration = self._get_configuration(conf_file, registry_configuration)
        return
    
    def _add_missing_keys(self, configuration: Dict, conf_file: Union[Path, str]):
        defaults = yaml.safe_load(open(conf_file))
        configuration.update({k: v for k, v in defaults.items() if k not in list(configuration.keys())})
        return configuration

    def _get_configuration(self, conf_file: Union[Path, str], registry_configuration: Dict) -> Union[Dict[str, Any]]:
        configuration = {}

        if registry_configuration:
            configuration = registry_configuration.copy()

        if not conf_file:
            configuration = self._add_missing_keys(configuration=configuration, conf_file=self._get_full_conf_path())
        else: 
            try:
                configuration = self._add_missing_keys(configuration=configuration, conf_file=conf_file)
            except IOError as io_error:
                logger.warning(
                    f"configuration file {conf_file} not found.  "
                    f"Using default config."
                )
                configuration = self._add_missing_keys(configuration=configuration, conf_file=self._get_full_conf_path())
            except Exception as yaml_error:
                print(f"Failed to parse file {conf_file}, resorting to default")
                configuration = self._add_missing_keys(configuration=configuration, conf_file=self._get_full_conf_path())

        return configuration

    def _is_recognizer_enabled(self, recognizer: Union[Dict[str, Any], str]) -> bool:
        return not "enabled" in recognizer or recognizer["enabled"]

    def _get_recognizer_name(self, recognizer: Union[Dict[str, Any], str]) -> str:
        if isinstance(recognizer, str):
            return recognizer
        return recognizer["name"]

    def _get_recognizer_context(self, recognizer: Union[Dict[str, Any], str]) -> List[str]:
        if isinstance(recognizer, str):
            return None
        return recognizer.get("context", None)

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
        splits the recognizer list to predefined and custom. All recognizers are custom by default though type: 'custom' can be mentioned as well. 
        This function supports the previous format as well.
        """
        predefined =[]
        custom =[]

        predefined = [recognizer for recognizer in recognizers if isinstance(recognizer, str) or ("type" in recognizer and recognizer["type"] == "predefined")]
        custom = [recognizer for recognizer in recognizers if not isinstance(recognizer, str) and ("type" not in recognizer or recognizer["type"] == "custom")]
        return predefined, custom

    def _create_custom_recognizers(self, recognizer: Dict) -> List[EntityRecognizer]:
        # legacy recognizer
        if "supported_language" in recognizer:
            return [PatternRecognizer.from_dict(recognizer)]

        recognizers = []

        for supported_language in self._get_recognizer_languages(recognizer):
            copied_recognizer = {k: v for k, v in recognizer.items() if k not in ["enabled", "type", "supported_languages"]}
            recognizers.append(PatternRecognizer.from_dict({**copied_recognizer, **supported_language}))

        return recognizers
    
    default_values = {
        "supported_languages": ["en"],
        "recognizers": [],
        "global_regex_flags": re.DOTALL | re.MULTILINE | re.IGNORECASE
    }

    def create_recognizer_registry(self) -> RecognizerRegistry:
        fields = {
            "supported_languages": None,
            "recognizers": None,
            "global_regex_flags": None
        }

        for field in fields.keys():
            if field not in self.configuration:
                logger.warning(f'{field} not present in configuration, using default value instead: {self.default_values[field]}')
            fields[field] = self.configuration.get(field, self.default_values[field])

        self.supported_languages = fields["supported_languages"]

        recognizer_instances = []
        predefined, custom = self._split_recognizers(fields["recognizers"])
        for recognizer in predefined:
            for language in self._get_recognizer_languages(recognizer):
                if self._is_recognizer_enabled(recognizer):
                    copied_recognizer = {k: v for k, v in self._get_recognizer_items(recognizer) if k not in ["enabled", "type", "supported_languages", "name"]}
                    recognizer_instances.append(getattr(presidio_analyzer.predefined_recognizers, self._get_recognizer_name(recognizer), None)(**{**copied_recognizer, **language}))

        for recognizer in custom:
            if self._is_recognizer_enabled(recognizer):
                recognizer_instances.extend(self._create_custom_recognizers(recognizer))

        for recognizer in recognizer_instances:
            if isinstance(recognizer, PatternRecognizer):
                recognizer.global_regex_flags = fields["global_regex_flags"]

        fields["recognizers"] = recognizer_instances

        return RecognizerRegistry(**fields)

    @staticmethod
    def _get_full_conf_path(
        default_conf_file: Union[Path, str] = "default_recognizers.yaml"
    ) -> Path:
        """Return a Path to the default conf file."""
        return Path(Path(__file__).parent.parent, "conf", default_conf_file)