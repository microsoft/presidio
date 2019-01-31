from abc import ABC, abstractmethod
import logging
import os
import tldextract

class EntityRecognizer:

    def __init__(self, supported_entities, supported_languages, version):
        """

        :param supported_entities: the supported entities of the recognizer
        :param supported_languages: the supported languages of the recognizer
        :param version: the recognizer current version
        """
        self.supported_entities = supported_entities
        self.supported_languages = supported_languages
        self.version = version

        loglevel = os.environ.get("LOG_LEVEL", "INFO")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)
        logging.getLogger('tldextract').setLevel(loglevel)

        # Caching top level domains
        tldextract.extract("")

    @abstractmethod
    def load(self):
          pass

    @abstractmethod
    def analyze_text(self, text, entities):
        """
                This is the core method for analyzing text, assuming field_types are
                the subset of the supported field types.
                :return: list of TextMatcherResult per found result
                :param text: text to be analyzed
                :param entities: list of entities to be detected
        """

        return None

    def get_supported_entities(self):
        return self.supported_entities

    def get_supported_languages(self):
        return self.supported_languages

    def get_version(self):
        return self.version
