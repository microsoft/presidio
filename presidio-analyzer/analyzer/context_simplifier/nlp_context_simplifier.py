import os
import logging
import spacy
from analyzer.context_simplifier.context_simplifier import ContextSimplifier


class NLPContextSimplifier(ContextSimplifier):
    """ NLPContextSimplifier is responsible for preprocessing the context text
        before the different recognizers use the context to get better
        confidence on the score. It uses a NLP model to Rremove punctuation,
        stop words and take lemma form and remove duplicates
    """

    def __init__(self):
        super().__init__()
        loglevel = os.environ.get("LOG_LEVEL", "INFO")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)

        self.logger.info("Loading NLP model (simplifier)...")
        self.nlp = spacy.load("en_core_web_lg", disable=['parser', 'tagger'])

    def simplify(self, context):
        """ simplifiy the given context and return a simpler version
        """
        nlp_context = self.nlp(context)

        # Remove punctuation, stop words and take lemma form and remove
        # duplicates
        keywords = list(
            filter(
                lambda k: not self.nlp.vocab[k.text].is_stop and
                not k.is_punct and
                k.lemma_ != '-PRON-' and
                k.lemma_ != 'be',
                nlp_context))
        keywords = list(set(map(lambda k: k.lemma_.lower(), keywords)))

        return keywords
