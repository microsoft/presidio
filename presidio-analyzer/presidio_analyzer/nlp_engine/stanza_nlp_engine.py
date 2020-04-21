import string

try:
    import stanza
except ImportError:
    stanza = None

from presidio_analyzer import PresidioLogger
from presidio_analyzer.nlp_engine import NlpArtifacts, NlpEngine

logger = PresidioLogger()


class StanzaNlpEngine(NlpEngine):
    """ StanzaNlpEngine is an abstraction layer over the nlp module.
        It provides processing functionality as well as other queries
        on tokens.
        The StanzaNlpEngine uses Stanza as its NLP module
    """

    engine_name = "stanza"
    is_available = True if stanza else False

    def __init__(self, models={"en": "en"}):
        logger.debug(f"Loading NLP models: {models.values()}")

        self.nlp = {
            lang: stanza.Pipeline(model_name, processors="tokenize,mwt,pos,lemma,ner")
            for lang, model_name in models.items()
        }

        for lang, model in self.nlp.items():
            logger.debug(f"Stanza model {lang} details: {model}")

    def process_text(self, text, language):
        """ Execute the Stanza NLP pipeline on the given text
            and language
        """
        doc = self.nlp[language](text)
        return self.doc_to_nlp_artifact(doc, language)

    def is_stopword(self, word, language):
        """ currenlty not used and always returns False
        """
        return False

    def is_punct(self, word, language):
        """ returns true if the given word is a punctuation word
            (within the given language)
        """
        return word in string.punctuation

    def get_nlp(self, language):
        return self.nlp[language]

    def doc_to_nlp_artifact(self, doc, language):
        tokens, lemmas, tokens_indices = zip(
            *[
                (w.text, w.lemma, self._process_stanza_word(w))
                for s in doc.sentences for w in s.words
            ]
        )
        entities = [e for s in doc.sentences for e in s.ents]
        return NlpArtifacts(entities=entities, tokens=tokens,
                            tokens_indices=tokens_indices, lemmas=lemmas,
                            nlp_engine=self, language=language)

    @staticmethod
    def _process_stanza_word(w):
        x = [idx.split("=") for idx in w.misc.split("|")]
        x = [(idx[0], int(idx[1])) for idx in x]
        x_dict = dict(x)
        return x_dict["start_char"]
