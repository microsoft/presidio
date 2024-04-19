import yaml
import logging
from pathlib import Path
from typing import Optional, Union, List, Dict, Any

from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import NlpEngineProvider, NlpEngine
from presidio_analyzer.recognizer_registry_provider import RecognizerRegistryProvider

logger = logging.getLogger("presidio-analyzer")


class AnalyzerEngineProvider:
    """
    Utility function for loading Presidio Analyzer.

    Use this class to load presidio analyzer engine from a yaml file
    """

    def __init__(self, conf_file: Optional[Union[Path, str]] = None):
        self.configuration = self._get_configuration(conf_file=conf_file)
        return

    def _get_configuration(self,
                           conf_file: Union[Path, str]
                           ) -> Union[Dict[str, Any]]:
        configuration = {}

        if not conf_file:
            configuration = yaml.safe_load(open(self._get_full_conf_path()))
        else:
            try:
                configuration = yaml.safe_load(open(conf_file))
            except IOError:
                logger.warning(
                    f"configuration file {conf_file} not found.  "
                    f"Using default config."
                )
                configuration = yaml.safe_load(open(self._get_full_conf_path()))
            except Exception:
                print(f"Failed to parse file {conf_file}, resorting to default")
                configuration = yaml.safe_load(open(self._get_full_conf_path()))

        return configuration

    def create_engine(self) -> AnalyzerEngine:
        """
        Load Presidio Analyzer from yaml configuration file.

        :return: analyzer engine initialized with yaml configuration
        """

        nlp_engine = self._load_nlp_engine()
        supported_languages = self.configuration.get("supported_languages", ["en"])
        default_score_threshold = self.configuration.get("default_score_threshold", 0)

        registry = self._load_recognizer_registry(supported_languages)

        analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine,
            registry=registry,
            supported_languages=supported_languages,
            default_score_threshold=default_score_threshold
        )

        analyzer.registry.add_nlp_recognizer(nlp_engine=analyzer.nlp_engine)

        return analyzer

    def _load_recognizer_registry(self,
                                  supported_languages: Optional[List[str]] = None
                                  ) -> RecognizerRegistry:
        if "recognizer_registry" not in self.configuration:
            logger.warning(
                "configuration file is missing 'recognizer_registry'. "
                "Using default configuration for recognizer registry"
            )
        registry_configuration = self.configuration.get("recognizer_registry", {})
        provider = RecognizerRegistryProvider(
            registry_configuration={**registry_configuration,
                                    "supported_languages": supported_languages})
        return provider.create_recognizer_registry()

    def _load_nlp_engine(self) -> Optional[NlpEngine]:
        if "nlp_configuration" not in self.configuration:
            logger.warning(
                "configuration file is missing 'nlp_configuration'."
                "Using default configuration for nlp engine"
            )
            return None
        nlp_configuration = self.configuration["nlp_configuration"]
        provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
        return provider.create_engine()

    @staticmethod
    def _get_full_conf_path(
        default_conf_file: Union[Path, str] = "default_analyzer.yaml"
    ) -> Path:
        """Return a Path to the default conf file."""
        return Path(Path(__file__).parent, "conf", default_conf_file)
