try:
    import stanza
    from spacy_stanza import StanzaLanguage
except ImportError:
    stanza = None

from presidio_analyzer import PresidioLogger
from presidio_analyzer.nlp_engine import SpacyNlpEngine

logger = PresidioLogger()


# pylint: disable=super-init-not-called
class StanzaNlpEngine(SpacyNlpEngine):
    """ StanzaNlpEngine is an abstraction layer over the nlp module.
        It provides processing functionality as well as other queries
        on tokens.
        The StanzaNlpEngine uses spacy-stanza and stanza as its NLP module
    """

    engine_name = "stanza"
    is_available = bool(stanza)

    def __init__(self, models=None):
        if not models:
            models = {"en": "en"}
        logger.debug(f"Loading Stanza models: {models.values()}")

        self.nlp = {
            lang_code: StanzaLanguage(
                stanza.Pipeline(
                    model_name,
                    processors="tokenize,pos,lemma,ner",
                )
            )
            for lang_code, model_name in models.items()
        }
