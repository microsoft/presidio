import spacy

from presidio_analyzer import PresidioLogger
from presidio_analyzer.nlp_engine import NlpArtifacts, NlpEngine

logger = PresidioLogger()


class SpacyNlpEngine(NlpEngine):
    """ SpacyNlpEngine is an abstraction layer over the nlp module.
        It provides processing functionality as well as other queries
        on tokens.
        The SpacyNlpEngine uses SpaCy as its NLP module
    """

    engine_name = "spacy"
    is_available = bool(spacy)

    def __init__(self, models=None):
        if not models:
            models = {"en": "en_core_web_lg"}
        logger.debug(f"Loading SpaCy models: {models.values()}")

        self.nlp = {
            lang_code: spacy.load(model_name, disable=['parser', 'tagger'])
            for lang_code, model_name in models.items()
        }

        for model_name in models.values():
            logger.debug("Printing spaCy model and package details:"
                         "\n\n {}\n\n".format(spacy.info(model_name)))

    def process_text(self, text, language):
        """ Execute the SpaCy NLP pipeline on the given text
            and language
        """
        doc = self.nlp[language](text)
        return self.doc_to_nlp_artifact(doc, language)

    def is_stopword(self, word, language):
        """ returns true if the given word is a stop word
            (within the given language)
        """
        return self.nlp[language].vocab[word].is_stop

    def is_punct(self, word, language):
        """ returns true if the given word is a punctuation word
            (within the given language)
        """
        return self.nlp[language].vocab[word].is_punct

    def get_nlp(self, language):
        return self.nlp[language]

    def doc_to_nlp_artifact(self, doc, language):
        tokens = [token.text for token in doc]
        lemmas = [token.lemma_ for token in doc]
        tokens_indices = [token.idx for token in doc]
        entities = doc.ents
        return NlpArtifacts(entities=entities, tokens=tokens,
                            tokens_indices=tokens_indices, lemmas=lemmas,
                            nlp_engine=self, language=language)
