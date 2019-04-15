import logging
import os

import spacy

from analyzer import NlpArtifacts
from analyzer.nlp_engine.nlp_engine import NlpEngine


class SpacyNlpEngine(NlpEngine):
    """ NlpLoader
    """

    def __init__(self):
        loglevel = os.environ.get("LOG_LEVEL", "INFO")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)

        self.logger.info("Loading NLP model...")
        self.nlp = {"english": spacy.load("en_core_web_lg",
                                          disable=['parser', 'tagger'])}

    def process_text(self, text, language):
        doc = self.nlp[language](text)
        return self.doc_to_nlp_artifact(doc)

    def is_stopword(self, word, language):
        return self.nlp[language].vocab[word].is_stop

    def get_nlp(self, language):
        return self.nlp[language]

    def doc_to_nlp_artifact(self, doc):
        tokens = [token.text for token in doc]
        lemmas = [token.lemma for token in doc]
        entities = doc.ents
        return NlpArtifacts(entities=entities, tokens=tokens, lemmas=lemmas,
                            nlp_entine=self)
