from __future__ import annotations

import logging
import re
from collections.abc import ItemsView
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union

import yaml

from presidio_analyzer import EntityRecognizer, PatternRecognizer
from presidio_analyzer.recognizer_registry import RecognizerRegistry

logger = logging.getLogger("presidio-analyzer")


class RecognizerRegistryProvider:
    r"""
    Utility class for loading Recognizer Registry.

    Use this class to load recognizer registry from a yaml file

    :param conf_file: Path to yaml file containing registry configuration
    :param registry_configuration: Dict containing registry configuration
    :example:
        {
            "supported_languages": ["de", "es"],
            "recognizers": [
                {
                    "name": "Zip code Recognizer",
                    "supported_language": "en",
                    "patterns": [
                        {
                            "name": "zip code (weak)",
                            "regex": "(\\b\\d{5}(?:\\-\\d{4})?\\b)",
                            "score": 0.01,
                        }
                    ],
                    "context": ["zip", "code"],
                    "supported_entity": "ZIP",
                }
            ]
        }
    """

    def __init__(
        self,
        conf_file: Optional[Union[Path, str]] = None,
        registry_configuration: Optional[Dict] = None,
    ):
        self.configuration = self._get_configuration(
            conf_file=conf_file, registry_configuration=registry_configuration
        )
        self.supported_languages = None
        self.all_existing_recognizers = self._get_all_existing_recognizers()
        return

    @staticmethod
    def _add_missing_keys(configuration: Dict, conf_file: Union[Path, str]) -> Dict:
        """
        Add missing keys to the configuration.

        Missing keys are added using the default configuration read from file.

        :param configuration: The configuration to update.
        :param conf_file: The configuration file to read from.
        """

        defaults = yaml.safe_load(open(conf_file))
        configuration.update(
            {k: v for k, v in defaults.items() if k not in list(configuration.keys())}
        )
        return configuration

    def _get_configuration(
        self, conf_file: Union[Path, str], registry_configuration: Dict
    ) -> Union[Dict[str, Any]]:
        """Get the configuration from the provided file or dict.

        :param conf_file: The configuration file
        to read the recognizer registry configuration from.
        :param registry_configuration: The configuration to use.
        """

        if conf_file and registry_configuration:
            raise ValueError(
                "Either conf_file or registry_configuration should"
                " be provided, not both."
            )

        configuration = {}

        if registry_configuration:
            configuration = registry_configuration.copy()

        if not conf_file:
            configuration = self._add_missing_keys(
                configuration=configuration, conf_file=self._get_full_conf_path()
            )
        else:
            try:
                configuration = self._add_missing_keys(
                    configuration=configuration, conf_file=conf_file
                )
            except OSError:
                logger.warning(
                    f"configuration file {conf_file} not found.  "
                    f"Using default config."
                )
                configuration = self._add_missing_keys(
                    configuration=configuration, conf_file=self._get_full_conf_path()
                )
            except Exception:
                logger.warning(
                    f"Failed to parse file {conf_file}, " f"resorting to default"
                )
                configuration = self._add_missing_keys(
                    configuration=configuration, conf_file=self._get_full_conf_path()
                )

        return configuration

    @staticmethod
    def _is_recognizer_enabled(recognizer_conf: Union[Dict[str, Any], str]) -> bool:
        return "enabled" not in recognizer_conf or recognizer_conf["enabled"]

    @staticmethod
    def _get_recognizer_name(recognizer_conf: Union[Dict[str, Any], str]) -> str:
        if isinstance(recognizer_conf, str):
            return recognizer_conf
        return recognizer_conf["name"]

    @staticmethod
    def _get_recognizer_context(
        recognizer: Union[Dict[str, Any], str],
    ) -> Optional[List[str]]:
        if isinstance(recognizer, str):
            return None
        return recognizer.get("context", None)

    @staticmethod
    def _get_recognizer_items(
        recognizer_conf: Union[Dict[str, Any], str],
    ) -> Union[dict[Any, Any], ItemsView[str, Any]]:
        if isinstance(recognizer_conf, str):
            return {}
        return recognizer_conf.items()

    def _get_recognizer_languages(
        self, recognizer_conf: Union[Dict[str, Any], str]
    ) -> List[Dict[str, Any]]:
        """
        Get the different language properties for each recognizer.

        Creating a new recognizer for each supported language.
        If language wasn't specified, create a recognizer for each supported language.

        :param recognizer_conf: The aforementioned recognizer.
        :return: The list of recognizers in the supported languages.
        """
        if (
            isinstance(recognizer_conf, str)
            or "supported_languages" not in recognizer_conf
        ):
            return [
                {
                    "supported_language": language,
                    "context": self._get_recognizer_context(recognizer_conf),
                }
                for language in self.supported_languages
            ]

        if isinstance(recognizer_conf["supported_languages"][0], str):
            return [
                {"supported_language": language, "context": None}
                for language in recognizer_conf["supported_languages"]
            ]

        return [
            {
                "supported_language": language["language"],
                "context": language.get("context", None),
            }
            for language in recognizer_conf["supported_languages"]
        ]

    @staticmethod
    def _split_recognizers(
        recognizers_conf: Union[Dict[str, Any], str],
    ) -> Tuple[List[Union[str, Dict[str, Any]]], List[Union[str, Dict[str, Any]]]]:
        """
        Split the recognizer list to predefined and custom.

        All recognizers are custom by default though
        type: 'custom' can be mentioned as well.
        This function supports the previous format as well.

        :param recognizers_conf: The recognizers' configuration
        """

        predefined = [
            recognizer_conf
            for recognizer_conf in recognizers_conf
            if isinstance(recognizer_conf, str)
            or ("type" in recognizer_conf and recognizer_conf["type"] == "predefined")
        ]
        custom = [
            recognizer_conf
            for recognizer_conf in recognizers_conf
            if not isinstance(recognizer_conf, str)
            and ("type" not in recognizer_conf or recognizer_conf["type"] == "custom")
        ]
        return predefined, custom

    def _create_custom_recognizers(
        self, recognizer_conf: Dict
    ) -> List[PatternRecognizer]:
        """Create a custom recognizer for each language, based on the provided conf."""
        # legacy recognizer
        if "supported_language" in recognizer_conf:
            return [PatternRecognizer.from_dict(recognizer_conf)]

        recognizers = []

        for supported_language in self._get_recognizer_languages(recognizer_conf):
            copied_recognizer = {
                k: v
                for k, v in recognizer_conf.items()
                if k not in ["enabled", "type", "supported_languages"]
            }
            kwargs = {**copied_recognizer, **supported_language}
            recognizers.append(PatternRecognizer.from_dict(kwargs))

        return recognizers

    default_values = {
        "supported_languages": ["en"],
        "recognizers": [],
        "global_regex_flags": re.DOTALL | re.MULTILINE | re.IGNORECASE,
    }

    def create_recognizer_registry(self) -> RecognizerRegistry:
        """Create a recognizer registry according to configuration loaded previously."""
        fields = {
            "supported_languages": None,
            "recognizers": None,
            "global_regex_flags": None,
        }

        for field in fields:
            if field not in self.configuration:
                logger.warning(
                    f"{field} not present in configuration, "
                    f"using default value instead: {self.default_values[field]}"
                )
            fields[field] = self.configuration.get(field, self.default_values[field])

        self.supported_languages = fields["supported_languages"]

        recognizer_instances = []
        predefined, custom = self._split_recognizers(fields["recognizers"])
        for recognizer_conf in predefined:
            for language_conf in self._get_recognizer_languages(recognizer_conf):
                if self._is_recognizer_enabled(recognizer_conf):
                    copied_recognizer_conf = {
                        k: v
                        for k, v in self._get_recognizer_items(recognizer_conf)
                        if k not in ["enabled", "type", "supported_languages", "name"]
                    }
                    kwargs = {**copied_recognizer_conf, **language_conf}
                    recognizer_name = self._get_recognizer_name(recognizer_conf)
                    recognizer_cls = self._get_existing_recognizer_cls_by_name(
                        recognizer_name
                    )
                    recognizer_instances.append(recognizer_cls(**kwargs))

        for recognizer_conf in custom:
            if self._is_recognizer_enabled(recognizer_conf):
                recognizer_instances.extend(
                    self._create_custom_recognizers(recognizer_conf)
                )

        for recognizer_conf in recognizer_instances:
            if isinstance(recognizer_conf, PatternRecognizer):
                recognizer_conf.global_regex_flags = fields["global_regex_flags"]

        recognizer_instances = [
            recognizer
            for recognizer in recognizer_instances
            if recognizer.supported_language in self.supported_languages
        ]

        fields["recognizers"] = recognizer_instances

        return RecognizerRegistry(**fields)

    @staticmethod
    def _get_full_conf_path(
        default_conf_file: Union[Path, str] = "default_recognizers.yaml",
    ) -> Path:
        """Return a Path to the default conf file."""
        return Path(Path(__file__).parent, "../conf", default_conf_file)

    @staticmethod
    def _get_all_existing_recognizers(
        cls: Optional[Type[EntityRecognizer]] = None,
    ) -> Set[Type[EntityRecognizer]]:
        """
        Return all subclasses of EntityRecognizer, recursively.

        :param cls: The initial class, if None, cls=EntityRecognizer.
        """

        if not cls:
            cls = EntityRecognizer

        return set(cls.__subclasses__()).union(
            [
                s
                for c in cls.__subclasses__()
                for s in RecognizerRegistryProvider._get_all_existing_recognizers(c)
            ]
        )

    def _get_existing_recognizer_cls_by_name(
        self, recognizer_name: str
    ) -> Type[EntityRecognizer]:
        """
        Get the recognizer class by name.

        Returns the requested recognizer class out of the list of all existing
        recognizers currently inheriting from EntityRecognizer.
        Raises a ValueError if the recognizer is not found.

        :param recognizer_name: The name of the recognizer.
        """
        for recognizer in self.all_existing_recognizers:
            if recognizer_name == recognizer.__name__:
                return recognizer

        raise ValueError(
            f"Recognizer of name {recognizer_name} was not found in the "
            f"list of recognizers inheriting the EntityRecognizer class"
        )
