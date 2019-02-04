import logging
import os
from abc import abstractmethod


class EntityRecognizer:

    def __init__(self, supported_entities, supported_languages=["en"], version="0.01"):
        """
        An abstract class to be inherited by Recognizers which hold the logic for recognizing specific PII entities.

        :param supported_entities: the entities supported by this recognizer (for example, phone number, address, etc.)
        :param supported_languages: the languages supported by this recognizer
        :param version: the recognizer current version
        """
        self.supported_entities = supported_entities
        self.supported_languages = supported_languages
        self.version = version

        loglevel = os.environ.get("LOG_LEVEL", "INFO")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)

        self.load()

    @abstractmethod
    def load(self):
        """
        Initialize the recognizer assets if needed (e.g. machine learning models)
        """
        pass

    @abstractmethod
    def analyze_text(self, text, entities):
        """
        This is the core method for analyzing text, assuming entities are
        the subset of the supported entities types.

        :param text: The text to be analyzed
        :param entities: The list of entities to be detected
        :return: list of RecognizerResult
        :rtype: [RecognizerResult]
        """

        return None

    def get_supported_entities(self):
        """
        :return: A list of the supported entities by this recognizer
        """
        return self.supported_entities

    def get_supported_languages(self):
        """
        :return: A list of the supported languages by this recognizer
        """
        return self.supported_languages

    def get_version(self):
        """
        :return: The current version of this recognizer
        """
        return self.version

    def to_dict(self):
        return __dict__

    @classmethod
    def from_dict(cls, data):
        cls(supported_entities=data.get('supported_entities'),
            supported_languages=data.get('supported_languages'),
            version=data.get("version"))
