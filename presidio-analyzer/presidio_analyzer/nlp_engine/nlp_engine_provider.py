import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import yaml

from presidio_analyzer.nlp_engine import (
    NerModelConfiguration,
    NlpEngine,
    SpacyNlpEngine,
    StanzaNlpEngine,
    TransformersNlpEngine,
)

logger = logging.getLogger("presidio-analyzer")


class NlpEngineProvider:
    """Create different NLP engines from configuration.

    :param nlp_engines: List of available NLP engines.
    Default: (SpacyNlpEngine, StanzaNlpEngine)
    :param nlp_configuration: Dict containing nlp configuration
    :example: configuration:
            {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en",
                            "model_name": "en_core_web_lg"
                          }]
            }
    Nlp engine names available by default: spacy, stanza.
    :param conf_file: Path to yaml file containing nlp engine configuration.
    """

    def __init__(
        self,
        nlp_engines: Optional[Tuple] = None,
        conf_file: Optional[Union[Path, str]] = None,
        nlp_configuration: Optional[Dict] = None,
    ):
        if nlp_engines:
            self._validate_nlp_engines(nlp_engines)
        else:
            nlp_engines = (SpacyNlpEngine, StanzaNlpEngine, TransformersNlpEngine)

        self.nlp_engines = {
            engine.engine_name: engine for engine in nlp_engines if engine.is_available
        }
        logger.debug(
            f"Loaded these available nlp engines: {list(self.nlp_engines.keys())}"
        )

        if conf_file and nlp_configuration:
            raise ValueError(
                "Either conf_file or nlp_configuration should be provided, not both."
            )

        if nlp_configuration:
            self._validate_nlp_configuration(nlp_configuration)
            self.nlp_configuration = nlp_configuration

        if conf_file or conf_file == '':
            self._validate_conf_file_path(conf_file)
            self.nlp_configuration = self._read_nlp_conf(conf_file)

        if conf_file is None and nlp_configuration is None:
            conf_file = self._get_full_conf_path()
            logger.debug(f"Reading default conf file from {conf_file}")
            self.nlp_configuration = self._read_nlp_conf(conf_file)

    @staticmethod
    def _validate_nlp_engines(nlp_engines: Tuple) -> None:
        """
        Validate that all NLP engine classes have the required attributes.

        :param nlp_engines: Tuple of NLP engine classes to validate.
        """

        if not isinstance(nlp_engines, tuple):
            raise ValueError(f"nlp_engines must be a tuple, got {type(nlp_engines)}")

        required_attributes = ['engine_name', 'is_available']

        for engine_class in nlp_engines:
            missing_attributes = []

            for attr in required_attributes:
                if not hasattr(engine_class, attr):
                    missing_attributes.append(attr)

            if missing_attributes:
                raise ValueError(
                    f"NLP engine class {engine_class} is missing required "
                    f"class attributes: {missing_attributes}. "
                    "All NLP engine classes must have 'engine_name' and 'is_available' "
                    "as class attributes."
                )

            if not isinstance(engine_class.engine_name, str):
                raise ValueError(
                    f"NLP engine class {engine_class} has invalid "
                    f"'engine_name' attribute. Expected string, "
                    f"got {type(engine_class.engine_name)}."
                )

            if not isinstance(engine_class.is_available, bool):
                raise ValueError(
                    f"NLP engine class {engine_class} has invalid "
                    f"'is_available' attribute. Expected boolean, "
                    f"got {type(engine_class.is_available)}."
                )

    @staticmethod
    def _validate_nlp_configuration(nlp_configuration: Dict) -> None:
        """
        Validate the NLP configuration structure and content.

        :param nlp_configuration: The configuration dictionary to validate
        """
        if not isinstance(nlp_configuration, Dict):
            raise ValueError(f"nlp_configuration must be a dictionary, "
                             f"got {type(nlp_configuration)}")

        required_fields = ['nlp_engine_name', 'models']
        missing_fields = []

        for field in required_fields:
            if field not in nlp_configuration.keys():
                missing_fields.append(field)

        if missing_fields:
            raise ValueError(
                f"nlp_configuration is missing required fields: {missing_fields}. "
                f"Required fields are: {required_fields}"
            )

    @staticmethod
    def _validate_conf_file_path(conf_file: Union[Path, str]) -> None:
        """
        Validate the conf file path.

        :param conf_file: The conf file path to validate
        """

        if conf_file == '':
            raise ValueError("conf_file is empty")

        if not isinstance(conf_file, (Path, str)):
            raise ValueError(f"conf_file must be a string or Path, "
                             f"got {type(conf_file)}")

        if not Path(conf_file).exists():
            raise ValueError(f"conf_file {conf_file} does not exist")

        if Path(conf_file).is_dir():
            raise ValueError(f"conf_file {conf_file} is a directory, not a file")

    def create_engine(self) -> NlpEngine:
        """Create an NLP engine instance."""
        if (
            not self.nlp_configuration
            or not self.nlp_configuration.get("models")
            or not self.nlp_configuration.get("nlp_engine_name")
        ):
            raise ValueError(
                "Illegal nlp configuration. "
                "Configuration should include nlp_engine_name and models "
                "(list of model_name for each lang_code)."
            )
        nlp_engine_name = self.nlp_configuration["nlp_engine_name"]
        if nlp_engine_name not in self.nlp_engines:
            raise ValueError(
                f"NLP engine '{nlp_engine_name}' is not available. "
                "Make sure you have all required packages installed"
            )
        try:
            nlp_engine_class = self.nlp_engines[nlp_engine_name]
            nlp_models = self.nlp_configuration["models"]

            ner_model_configuration = self.nlp_configuration.get(
                "ner_model_configuration"
            )
            if ner_model_configuration:
                ner_model_configuration = NerModelConfiguration.from_dict(
                    ner_model_configuration
                )

            engine = nlp_engine_class(
                models=nlp_models, ner_model_configuration=ner_model_configuration
            )
            engine.load()
            logger.info(
                f"Created NLP engine: {engine.engine_name}. "
                f"Loaded models: {list(engine.nlp.keys())}"
            )
            return engine
        except KeyError:
            raise ValueError("Wrong NLP engine configuration")

    @staticmethod
    def _read_nlp_conf(conf_file: Union[Path, str]) -> dict:
        """
        Read the nlp configuration from a provided yaml file.

        :param conf_file: The conf file path to read
        """

        with open(conf_file) as file:
            nlp_configuration = yaml.safe_load(file)

        if "ner_model_configuration" not in nlp_configuration:
            logger.warning(
                "configuration file is missing 'ner_model_configuration'. Using default"
            )

        return nlp_configuration

    @staticmethod
    def _get_full_conf_path(
        default_conf_file: Union[Path, str] = "default.yaml",
    ) -> Path:
        """Return a Path to the default conf file."""
        return Path(Path(__file__).parent.parent, "conf", default_conf_file)
