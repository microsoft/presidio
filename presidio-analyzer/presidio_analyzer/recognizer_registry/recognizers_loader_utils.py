from __future__ import annotations

import inspect
import logging
from collections.abc import ItemsView
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

import yaml

from presidio_analyzer import EntityRecognizer, PatternRecognizer

logger = logging.getLogger("presidio-analyzer")


class PredefinedRecognizerNotFoundError(Exception):
    """Exception raised when a predefined recognizer is not found."""

    pass


class RecognizerListLoader:
    """A utility class that initializes recognizers based on configuration."""

    SUPPORTED_ENTITY: ClassVar[str] = "supported_entity"
    SUPPORTED_ENTITIES: ClassVar[str] = "supported_entities"

    @staticmethod
    def _get_recognizer_items(
        recognizer_conf: Union[Dict[str, Any], str],
    ) -> Union[dict[Any, Any], ItemsView[str, Any]]:
        if isinstance(recognizer_conf, str):
            return {}
        return recognizer_conf.items()

    @staticmethod
    def is_recognizer_enabled(recognizer_conf: Union[Dict[str, Any], str]) -> bool:
        """Return True if the recognizer is enabled.

        :param recognizer_conf: The recognizer configuration.
        """
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
            if isinstance(recognizer_conf, dict)
            and ("type" in recognizer_conf and recognizer_conf["type"] == "predefined")
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
            or recognizer_conf["supported_languages"] is None
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
    def get_recognizer_name(recognizer_conf: Union[Dict[str, Any], str]) -> str:
        """Get the class name for recognizer instantiation.

        Uses 'class_name' if present, otherwise 'name'.

        Logic:
        - If only 'name' exists: Use 'name' as both class name (for instantiation)
          and instance name (passed to __init__)
        - If 'class_name' exists: Use 'class_name' for instantiation and 'name'
          as the instance name (passed to __init__)

        :param recognizer_conf: The recognizer configuration.
        """
        if isinstance(recognizer_conf, str):
            return recognizer_conf
        class_name = recognizer_conf.get("class_name")
        if class_name:
            return class_name
        return recognizer_conf["name"]

    @staticmethod
    def _convert_supported_entities_to_entity(conf: Dict[str, Any]) -> None:
        if RecognizerListLoader.SUPPORTED_ENTITIES in conf:
            supported_entities = conf.pop(RecognizerListLoader.SUPPORTED_ENTITIES)
            if RecognizerListLoader.SUPPORTED_ENTITY not in conf and supported_entities:
                conf[RecognizerListLoader.SUPPORTED_ENTITY] = supported_entities[0]

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
        # legacy recognizer (has supported_language set to a value, not None)
        if recognizer_conf.get("supported_language"):
            # Remove supported_languages field (plural) if present,
            # as we're using supported_language (singular)
            conf_copy = {
                k: v for k, v in recognizer_conf.items() if k != "supported_languages"
            }

            # Transform supported_entities -> supported_entity
            # (PatternRecognizer expects singular)
            RecognizerListLoader._convert_supported_entities_to_entity(conf_copy)

            return [PatternRecognizer.from_dict(conf_copy)]

        recognizers = []

        for supported_language in RecognizerListLoader._get_recognizer_languages(
            recognizer_conf=recognizer_conf, supported_languages=supported_languages
        ):
            copied_recognizer = {
                k: v
                for k, v in recognizer_conf.items()
                if k not in ["enabled", "type", "supported_languages"]
            }

            # Transform supported_entities -> supported_entity
            # (PatternRecognizer expects singular)
            RecognizerListLoader._convert_supported_entities_to_entity(
                copied_recognizer
            )

            kwargs = {**copied_recognizer, **supported_language}
            recognizers.append(PatternRecognizer.from_dict(kwargs))

        return recognizers

    @staticmethod
    def get_all_existing_recognizers(
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
                for s in RecognizerListLoader.get_all_existing_recognizers(c)
            ]
        )

    @staticmethod
    def get_existing_recognizer_cls(recognizer_name: str) -> Type[EntityRecognizer]:
        """
        Get the recognizer class by name.

        Returns the requested recognizer class out of the list of all existing
        recognizers currently inheriting from EntityRecognizer.
        Raises a ValueError if the recognizer is not found.

        :param recognizer_name: The name of the recognizer.
        """
        all_existing_recognizers = RecognizerListLoader.get_all_existing_recognizers()
        for recognizer in all_existing_recognizers:
            if recognizer_name == recognizer.__name__:
                return recognizer

        raise PredefinedRecognizerNotFoundError(
            f"Recognizer of name {recognizer_name} was not found in the "
            f"list of recognizers inheriting the EntityRecognizer class"
        )

    @staticmethod
    def _prepare_recognizer_kwargs(
        recognizer_conf: Dict[str, Any],
        language_conf: Dict[str, Any],
        recognizer_cls: Type[EntityRecognizer],
    ) -> Dict[str, Any]:
        """
        Prepare kwargs for recognizer instantiation.

        This function adapts supported_entity/supported_entities based on the
        recognizer class __init__ signature to avoid passing unexpected kwargs.

        - If recognizer accepts only supported_entity (singular), convert
          supported_entities -> supported_entity (first element).
        - If recognizer accepts only supported_entities (plural), remove
          supported_entity.
        - If recognizer accepts both, keep keys as provided (after None cleanup).
        - Filtering policy:
            - supported_entity: kept only if explicitly accepted.
            - supported_entities: kept if explicitly accepted or if the recognizer
              accepts **kwargs.
        """
        kwargs = {**recognizer_conf, **language_conf}

        # Cleanup: Remove provided entity arguments if they are explicitly None
        if (
            RecognizerListLoader.SUPPORTED_ENTITY in kwargs
            and kwargs[RecognizerListLoader.SUPPORTED_ENTITY] is None
        ):
            kwargs.pop(RecognizerListLoader.SUPPORTED_ENTITY, None)

        if (
            RecognizerListLoader.SUPPORTED_ENTITIES in kwargs
            and kwargs[RecognizerListLoader.SUPPORTED_ENTITIES] is None
        ):
            kwargs.pop(RecognizerListLoader.SUPPORTED_ENTITIES, None)

        try:
            params = inspect.signature(recognizer_cls.__init__).parameters
        except (TypeError, ValueError):
            # Drop entity-related kwargs to avoid passing unexpected arguments when the
            # signature cannot be inspected.
            kwargs.pop(RecognizerListLoader.SUPPORTED_ENTITY, None)
            kwargs.pop(RecognizerListLoader.SUPPORTED_ENTITIES, None)
            return kwargs

        # If the recognizer accepts **kwargs, passing extra fields won't raise
        # TypeError. Whether the recognizer uses them is up to the implementation.
        has_var_kw = any(
            p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values()
        )

        accepts_supported_entity = RecognizerListLoader.SUPPORTED_ENTITY in params
        accepts_supported_entities = RecognizerListLoader.SUPPORTED_ENTITIES in params

        # 1. Normalize: Convert plural -> singular if needed
        # (Only when singular is accepted and plural is NOT accepted)
        if accepts_supported_entity and not accepts_supported_entities:
            if RecognizerListLoader.SUPPORTED_ENTITIES in kwargs:
                supported_entities = kwargs.get(RecognizerListLoader.SUPPORTED_ENTITIES)

                # Use the first entity if available
                if isinstance(supported_entities, list) and supported_entities:
                    kwargs.pop(RecognizerListLoader.SUPPORTED_ENTITIES)
                    kwargs.setdefault(
                        RecognizerListLoader.SUPPORTED_ENTITY, supported_entities[0]
                    )

        # 2. Filter: Remove keys that are NOT in the signature

        # For supported_entities (plural):
        # If not explicitly accepted, remove unless **kwargs is present (compat).
        if not accepts_supported_entities and not has_var_kw:
            kwargs.pop(RecognizerListLoader.SUPPORTED_ENTITIES, None)

        # Drop unsupported 'supported_entity' even for **kwargs
        # to prevent leaking into strict parent __init__.
        if not accepts_supported_entity:
            kwargs.pop(RecognizerListLoader.SUPPORTED_ENTITY, None)

        return kwargs

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

        predefined_to_exclude = {"enabled", "type", "supported_languages", "class_name"}
        custom_to_exclude = {"enabled", "type", "class_name"}
        for recognizer_conf in predefined:
            for language_conf in RecognizerListLoader._get_recognizer_languages(
                recognizer_conf=recognizer_conf, supported_languages=supported_languages
            ):
                if RecognizerListLoader.is_recognizer_enabled(recognizer_conf):
                    new_conf = RecognizerListLoader._filter_recognizer_fields(
                        recognizer_conf, to_exclude=predefined_to_exclude
                    )

                    recognizer_name = RecognizerListLoader.get_recognizer_name(
                        recognizer_conf=recognizer_conf
                    )
                    recognizer_cls = RecognizerListLoader.get_existing_recognizer_cls(
                        recognizer_name=recognizer_name
                    )

                    kwargs = RecognizerListLoader._prepare_recognizer_kwargs(
                        new_conf, language_conf, recognizer_cls
                    )

                    recognizer_instances.append(recognizer_cls(**kwargs))

        for recognizer_conf in custom:
            if RecognizerListLoader.is_recognizer_enabled(recognizer_conf):
                new_conf = RecognizerListLoader._filter_recognizer_fields(
                    recognizer_conf, to_exclude=custom_to_exclude
                )
                recognizer_instances.extend(
                    RecognizerListLoader._create_custom_recognizers(
                        recognizer_conf=new_conf,
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

    @staticmethod
    def _filter_recognizer_fields(
        recognizer_conf: Dict[str, Any], to_exclude: Set[str]
    ) -> Dict[str, Any]:
        copied_recognizer_conf = {
            k: v
            for k, v in RecognizerListLoader._get_recognizer_items(
                recognizer_conf=recognizer_conf
            )
            if k not in to_exclude
        }
        return copied_recognizer_conf


class RecognizerConfigurationLoader:
    """A utility class that initializes recognizer registry configuration."""

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

        # Validation is now handled by Pydantic via ConfigurationValidator
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
        config_from_file = {}
        use_defaults = True

        if registry_configuration:
            configuration = registry_configuration.copy()
            # Check if registry_configuration has all mandatory keys
            # Note: supported_languages is now optional,
            # so we only check for recognizers
            mandatory_keys_set = {"recognizers", "global_regex_flags"}
            config_keys = set(configuration.keys())
            if mandatory_keys_set.issubset(config_keys):
                use_defaults = False

        if conf_file:
            try:
                with open(conf_file) as file:
                    config_from_file = yaml.safe_load(file)
                use_defaults = False

            except OSError:
                logger.warning(
                    f"configuration file {conf_file} not found.  Using default config."
                )
                with open(RecognizerConfigurationLoader._get_full_conf_path()) as file:
                    config_from_file = yaml.safe_load(file)
                use_defaults = False

            except Exception as e:
                raise ValueError(f"Failed to parse file {conf_file}. Error: {str(e)}")

        # Load defaults if needed (no config provided,
        # or registry_configuration is incomplete)
        if use_defaults:
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

        # Check if config_from_file has any invalid keys
        # (keys that aren't mandatory or valid optional keys)
        # If it has keys but none of them are mandatory keys,
        # it's likely an invalid config
        if config_from_file and conf_file:
            config_keys = set(config_from_file.keys())
            mandatory_keys_set = {"recognizers"}  # Only recognizers is truly mandatory

            # If config has keys but none are mandatory and it's from a conf_file,
            # it's probably invalid - don't merge with defaults
            if config_keys and not config_keys.intersection(mandatory_keys_set):
                raise ValueError(
                    f"Configuration file {conf_file} does not contain any of the "
                    f"mandatory keys: {list(mandatory_keys_set)}. "
                    f"Found keys: {list(config_keys)}"
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
