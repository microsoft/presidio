from __future__ import annotations

import logging
from collections.abc import ItemsView
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Type, Union

import yaml

from presidio_analyzer import EntityRecognizer, PatternRecognizer

logger = logging.getLogger("presidio-analyzer")


class RecognizerListLoader:
    """A utility class that initializes recognizers based on configuration."""

    @staticmethod
    def _get_recognizer_items(
        recognizer_conf: Union[Dict[str, Any], str],
    ) -> Union[dict[Any, Any], ItemsView[str, Any]]:
        if isinstance(recognizer_conf, str):
            return {}
        return recognizer_conf.items()

    @staticmethod
    def _is_recognizer_enabled(recognizer_conf: Union[Dict[str, Any], str]) -> bool:
        return "enabled" not in recognizer_conf or recognizer_conf["enabled"]

    @staticmethod
    def _get_recognizer_context(
        recognizer: Union[Dict[str, Any], str],
    ) -> Optional[List[str]]:
        if isinstance(recognizer, str):
            return None
        return recognizer.get("context", None)

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
            if ("type" in recognizer_conf and recognizer_conf["type"] == "predefined")
        ]
        custom = [
            recognizer_conf
            for recognizer_conf in recognizers_conf
            if not isinstance(recognizer_conf, str)
            and ("type" not in recognizer_conf or recognizer_conf["type"] == "custom")
        ]
        return predefined, custom

    @staticmethod
    def _get_recognizer_languages(
        recognizer_conf: Union[Dict[str, Any], str],
        supported_languages: Iterable[str],
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
                    "context": RecognizerListLoader._get_recognizer_context(
                        recognizer=recognizer_conf
                    ),
                }
                for language in supported_languages
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
    def _get_recognizer_name(recognizer_conf: Union[Dict[str, Any], str]) -> str:
        if isinstance(recognizer_conf, str):
            return recognizer_conf
        return recognizer_conf["name"]

    @staticmethod
    def _is_language_supported_globally(
        recognizer: EntityRecognizer,
        supported_languages: Iterable[str],
    ) -> bool:
        if recognizer.supported_language not in supported_languages:
            logger.warning(
                f"Recognizer not added to registry because "
                f"language is not supported by registry - "
                f"{recognizer.name} supported "
                f"languages: {recognizer.supported_language}"
                f", registry supported languages: "
                f"{', '.join(supported_languages)}"
            )
            return False
        return True

    @staticmethod
    def _create_custom_recognizers(
        recognizer_conf: Dict,
        supported_languages: Iterable[str],
    ) -> List[PatternRecognizer]:
        """Create a custom recognizer for each language, based on the provided conf."""
        # legacy recognizer
        if "supported_language" in recognizer_conf:
            return [PatternRecognizer.from_dict(recognizer_conf)]

        recognizers = []

        for supported_language in RecognizerListLoader._get_recognizer_languages(
            recognizer_conf=recognizer_conf, supported_languages=supported_languages
        ):
            copied_recognizer = {
                k: v
                for k, v in recognizer_conf.items()
                if k not in ["enabled", "type", "supported_languages"]
            }
            kwargs = {**copied_recognizer, **supported_language}
            recognizers.append(PatternRecognizer.from_dict(kwargs))

        return recognizers

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
                for s in RecognizerListLoader._get_all_existing_recognizers(c)
            ]
        )

    @staticmethod
    def _get_existing_recognizer_cls(recognizer_name: str) -> Type[EntityRecognizer]:
        """
        Get the recognizer class by name.

        Returns the requested recognizer class out of the list of all existing
        recognizers currently inheriting from EntityRecognizer.
        Raises a ValueError if the recognizer is not found.

        :param recognizer_name: The name of the recognizer.
        """
        all_existing_recognizers = RecognizerListLoader._get_all_existing_recognizers()
        for recognizer in all_existing_recognizers:
            if recognizer_name == recognizer.__name__:
                return recognizer

        raise ValueError(
            f"Recognizer of name {recognizer_name} was not found in the "
            f"list of recognizers inheriting the EntityRecognizer class"
        )

    @staticmethod
    def get(
        recognizers: Dict[str, Any],
        supported_languages: Iterable[str],
        global_regex_flags: int,
    ) -> Iterable[EntityRecognizer]:
        """
        Create an iterator of recognizers.

        The recognizers are initialized according to configuration loaded previously.
        """
        recognizer_instances = []
        predefined, custom = RecognizerListLoader._split_recognizers(recognizers)
        for recognizer_conf in predefined:
            for language_conf in RecognizerListLoader._get_recognizer_languages(
                recognizer_conf=recognizer_conf, supported_languages=supported_languages
            ):
                if RecognizerListLoader._is_recognizer_enabled(recognizer_conf):
                    copied_recognizer_conf = {
                        k: v
                        for k, v in RecognizerListLoader._get_recognizer_items(
                            recognizer_conf=recognizer_conf
                        )
                        if k not in ["enabled", "type", "supported_languages", "name"]
                    }
                    kwargs = {**copied_recognizer_conf, **language_conf}
                    recognizer_name = RecognizerListLoader._get_recognizer_name(
                        recognizer_conf=recognizer_conf
                    )
                    recognizer_cls = RecognizerListLoader._get_existing_recognizer_cls(
                        recognizer_name=recognizer_name
                    )
                    recognizer_instances.append(recognizer_cls(**kwargs))

        for recognizer_conf in custom:
            if RecognizerListLoader._is_recognizer_enabled(recognizer_conf):
                recognizer_instances.extend(
                    RecognizerListLoader._create_custom_recognizers(
                        recognizer_conf=recognizer_conf,
                        supported_languages=supported_languages,
                    )
                )

        for recognizer_conf in recognizer_instances:
            if isinstance(recognizer_conf, PatternRecognizer):
                recognizer_conf.global_regex_flags = global_regex_flags

        recognizer_instances = [
            recognizer
            for recognizer in recognizer_instances
            if RecognizerListLoader._is_language_supported_globally(
                recognizer=recognizer, supported_languages=supported_languages
            )
        ]

        return recognizer_instances


class RecognizerConfigurationLoader:
    """A utility class that initializes recognizer registry configuraton."""

    mandatory_keys = [
        "supported_languages",
        "recognizers",
        "global_regex_flags",
    ]

    @staticmethod
    def _merge_configuration(
        registry_configuration: Dict, config_from_file: Dict[str, Any]
    ) -> Dict:
        """
        Add missing keys to the configuration.

        Missing keys are added using the configuration read from file.
        :param registry_configuration: The configuration to update.
        :param config_from_file: The configuration coming from the conf file.
        """

        registry_configuration.update(
            {
                k: v
                for k, v in config_from_file.items()
                if k not in list(registry_configuration.keys())
            }
        )

        missing_keys = [
            key
            for key in RecognizerConfigurationLoader.mandatory_keys
            if key not in registry_configuration
        ]
        if len(missing_keys) > 0:
            raise ValueError(f"Missing the following keys: {', '.join(missing_keys)}")

        return registry_configuration

    @staticmethod
    def get(
        conf_file: Optional[Union[Path, str]] = None,
        registry_configuration: Optional[Dict] = None,
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

        if conf_file:
            try:
                with open(conf_file) as file:
                    config_from_file = yaml.safe_load(file)

            except OSError:
                logger.warning(
                    f"configuration file {conf_file} not found.  "
                    f"Using default config."
                )
                with open(RecognizerConfigurationLoader._get_full_conf_path()) as file:
                    config_from_file = yaml.safe_load(file)

            except Exception as e:
                raise ValueError(
                    f"Failed to parse file {conf_file}." f"Error: {str(e)}"
                )
        else:
            with open(RecognizerConfigurationLoader._get_full_conf_path()) as file:
                config_from_file = yaml.safe_load(file)

        if config_from_file and not isinstance(config_from_file, dict):
            raise TypeError(
                f"The configuration in file {conf_file} should be a valid YAML, "
                f"got {type(config_from_file)}"
            )

        if registry_configuration and not isinstance(registry_configuration, dict):
            raise TypeError(
                f"Expected registry_configuration to be a dict, "
                f"got {type(registry_configuration)}"
            )

        configuration = RecognizerConfigurationLoader._merge_configuration(
            registry_configuration=configuration, config_from_file=config_from_file
        )
        return configuration

    @staticmethod
    def _get_full_conf_path(
        default_conf_file: Union[Path, str] = "default_recognizers.yaml",
    ) -> Path:
        """Return a Path to the default conf file."""
        return Path(Path(__file__).parent, "../conf", default_conf_file)
