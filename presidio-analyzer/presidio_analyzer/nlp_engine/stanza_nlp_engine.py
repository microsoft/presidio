try:
    import stanza
    from spacy_stanza import StanzaLanguage
except ImportError:
    stanza = None

from presidio_analyzer import PresidioLogger
from presidio_analyzer.nlp_engine import SpacyNlpEngine

logger = PresidioLogger()


class StanzaNlpEngine(SpacyNlpEngine):
    """ StanzaNlpEngine is an abstraction layer over the nlp module.
        It provides processing functionality as well as other queries
        on tokens.
        The StanzaNlpEngine uses spacy-stanza and stanza as its NLP module
    """

    engine_name = "stanza"
    is_available = True if stanza else False

    def __init__(self, models={"en": "en"}):
        logger.debug(f"Loading NLP models: {models.values()}")

        self.nlp = {
            lang: StanzaLanguage(stanza.Pipeline(model_name, processors="tokenize,mwt,pos,lemma,ner")) 
            for lang, model_name in models.items()
        }

