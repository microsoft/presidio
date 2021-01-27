"""NLP engine package. Performs text pre-processing."""
from typing import Union

from .nlp_artifacts import NlpArtifacts
from .nlp_engine import NlpEngine
from .spacy_nlp_engine import SpacyNlpEngine
from .stanza_nlp_engine import StanzaNlpEngine
from .. import PresidioLogger

_all_engines = [SpacyNlpEngine, StanzaNlpEngine]


NLP_ENGINES = {
    engine.engine_name: engine for engine in _all_engines if engine.is_available
}

logger = PresidioLogger("presidio-analyzer")


def create_nlp_engine(
    nlp_configuration: dict,
) -> Union[SpacyNlpEngine, StanzaNlpEngine]:
    """
    Create an NLP engine instance given a configuration file.

    :param nlp_configuration: Dict containing configuration.
    Example configuration:
    {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en",
                    "model_name": "en_core_web_lg"
                  }]
    }
    """

    if (
        not nlp_configuration
        or not nlp_configuration["nlp_engine_name"]
        or not nlp_configuration["models"]
    ):
        raise ValueError(
            "Illegal nlp configuration. "
            "Configuration should include nlp_engine_name and models "
            "(list of model_name for each lang_code)."
        )

    nlp_engine_name = nlp_configuration["nlp_engine_name"]
    nlp_engine_class = NLP_ENGINES[nlp_engine_name]
    nlp_engine_opts = {
        m["lang_code"]: m["model_name"] for m in nlp_configuration["models"]
    }
    engine = nlp_engine_class(nlp_engine_opts)
    logger.info(f"{nlp_engine_class.__name__} created")
    return engine


__all__ = [
    "NlpArtifacts",
    "NlpEngine",
    "SpacyNlpEngine",
    "StanzaNlpEngine",
    "NLP_ENGINES",
    "create_nlp_engine",
]
