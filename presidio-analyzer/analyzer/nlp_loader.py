import os
import logging
import spacy


class NlpLoader:
    """ NlpLoader
    """

    def __init__(self):
        loglevel = os.environ.get("LOG_LEVEL", "INFO")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)

        self.logger.info("Loading NLP model...")
        self.nlp = spacy.load("en_core_web_lg", disable=['parser', 'tagger'])

    def get_nlp(self):
        return self.nlp
