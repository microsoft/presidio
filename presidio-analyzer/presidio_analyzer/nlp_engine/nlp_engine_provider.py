import logging
from pathlib import Path
from typing import Optional, Dict, Union, Tuple

import yaml

from presidio_analyzer.nlp_engine import StanzaNlpEngine, SpacyNlpEngine, NlpEngine

logger = logging.getLogger("presidio-analyzer")


class NlpEngineProvider:
    """Create different NLP engines from configuration.

    :param nlp_engines: List of available NLP engines.
    Default: (SpacyNlpEngine, StanzaNlpEngine)
    :param nlp_configuration: Dict containing nlp configuration
    Example configuration:
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

        if not nlp_engines:
            nlp_engines = (SpacyNlpEngine, StanzaNlpEngine)

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
            self.nlp_configuration = nlp_configuration

        if conf_file:
            self.nlp_configuration = self._read_nlp_conf(conf_file)

        if not conf_file and not nlp_configuration:
            conf_file = self._get_full_conf_path()
            logger.debug(f"Reading default conf file from {conf_file}")
            self.nlp_configuration = self._read_nlp_conf(conf_file)

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
        try:
            nlp_engine_name = self.nlp_configuration["nlp_engine_name"]
            nlp_engine_class = self.nlp_engines[nlp_engine_name]
            nlp_engine_opts = {
                m["lang_code"]: m["model_name"]
                for m in self.nlp_configuration["models"]
            }
            engine = nlp_engine_class(nlp_engine_opts)
            logger.info(
                f"Created NLP engine: {engine.engine_name}. "
                f"Loaded models: {list(engine.nlp.keys())}"
            )
            return engine
        except KeyError:
            raise ValueError("Wrong NLP engine configuration")

    @staticmethod
    def _read_nlp_conf(conf_file: Union[Path, str]) -> dict:
        """Read the nlp configuration from a provided yaml file."""

        if not Path(conf_file).exists():
            nlp_configuration = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
            }
            logger.warning(
                f"configuration file {conf_file} not found.  "
                f"Using default config: {nlp_configuration}."
            )

        else:
            nlp_configuration = yaml.safe_load(open(conf_file))

        return nlp_configuration

    @staticmethod
    def _get_full_conf_path(
        default_conf_file: Union[Path, str] = "default.yaml"
    ) -> Path:
        """Return a Path to the default conf file."""
        return Path(Path(__file__).parent.parent.parent, "conf", default_conf_file)
