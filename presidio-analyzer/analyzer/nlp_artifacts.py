import os
import logging


class NlpArtifacts():
    """ NlpArtifacts is an abstraction layer over the results of an NLP pipeline
        processing over a given text, it holds attributes such as entities
        which can be used by any recognizer
    """

    # pylint: disable=abstract-method, unused-argument
    def __init__(self, nlp_doc, **kwargs):
        loglevel = os.environ.get("LOG_LEVEL", "INFO")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)

        if not nlp_doc:
            self.logger.error("NLP document is None")
            return

        self.entities = nlp_doc.ents
        self.logger.info("Loaded NLP document")
