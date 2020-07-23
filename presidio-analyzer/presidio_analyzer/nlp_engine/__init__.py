# pylint: disable=unused-import
from .nlp_artifacts import NlpArtifacts  # noqa: F401
from .nlp_engine import NlpEngine  # noqa: F401
from .spacy_nlp_engine import SpacyNlpEngine  # noqa: F401
from .stanza_nlp_engine import StanzaNlpEngine  # noqa: F401

_all_engines = [SpacyNlpEngine, StanzaNlpEngine]

NLP_ENGINES = {
    engine.engine_name: engine
    for engine in _all_engines
    if engine.is_available
}
