import spacy
from spacy.cli import download

from analyzer.logger import Logger
from analyzer.nlp_engine import NlpArtifacts, NlpEngine
logger = Logger()


class SpacyNlpEngine(NlpEngine):
    """ SpacyNlpEngine is an abstraction layer over the nlp module.
        It provides processing functionality as well as other queries
        on tokens.
        The SpacyNlpEngine uses SpaCy as its NLP module
    """

    def __init__(self):
        logger.info("Loading NLP model...")

        # Download model lazily if it wasn't previously installed
        download('en_core_web_lg')
        self.nlp = {"en": spacy.load("en_core_web_lg",
                                     disable=['parser', 'tagger'])}

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
