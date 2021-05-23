import logging

try:
    import stanza
    import spacy_stanza
except ImportError:
    stanza = None

from presidio_analyzer.nlp_engine import SpacyNlpEngine

logger = logging.getLogger("presidio-analyzer")


class StanzaNlpEngine(SpacyNlpEngine):
    """
    StanzaNlpEngine is an abstraction layer over the nlp module.

    It provides processing functionality as well as other queries
    on tokens.
    The StanzaNlpEngine uses spacy-stanza and stanza as its NLP module

    :param models: Dictionary with the name of the stanza model per language.
    For example: models = {"en": "en"}
    """

    engine_name = "stanza"
    is_available = bool(stanza)

    def __init__(self, models=None):  # noqa ANN201
        if not models:
            models = {"en": "en"}
        logger.debug(f"Loading Stanza models: {models.values()}")

        self.nlp = {
            lang_code: spacy_stanza.load_pipeline(
                model_name,
                processors="tokenize,pos,lemma,ner",
            )
            for lang_code, model_name in models.items()
        }
