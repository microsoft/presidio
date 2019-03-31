import logging
import os
from abc import abstractmethod


class EntityRecognizer:
    MIN_SCORE = 0
    MAX_SCORE = 1.0

    def __init__(self, supported_entities, name=None, supported_language="en",
                 version="0.0.1"):
        """
        An abstract class to be inherited by Recognizers which hold the logic
         for recognizing specific PII entities.
        :param supported_entities: the entities supported by this recognizer
        (for example, phone number, address, etc.)
        :param supported_language: the language supported by this recognizer.
        The supported langauge code is iso6391Name
        :param name: the name of this recognizer (optional)
        :param version: the recognizer current version
        """
        self.supported_entities = supported_entities

        if name is None:
            self.name = self.__class__.__name__  # assign class name as name
        else:
            self.name = name

        self.supported_language = supported_language
        self.version = version
        self.is_loaded = False

        loglevel = os.environ.get("LOG_LEVEL", "INFO")
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(loglevel)
        self.load()
        logging.info("Loaded recognizer: %s", self.name)
        self.is_loaded = True

    @abstractmethod
    def load(self):
        """
        Initialize the recognizer assets if needed
        (e.g. machine learning models)
        """

    @abstractmethod
    def analyze(self, text, entities, simplifier):
        """
        This is the core method for analyzing text, assuming entities are
        the subset of the supported entities types.

        :param text: The text to be analyzed
        :param entities: The list of entities to be detected
        :param simplifier: makes the context easier to manage.
                           It transforms to singular form, remove punctuation,
                           etc...
        :return: list of RecognizerResult
        :rtype: [RecognizerResult]
        """

        return None

    def get_supported_entities(self):
        """
        :return: A list of the supported entities by this recognizer
        """
        return self.supported_entities

    def get_supported_language(self):
        """
        :return: A list of the supported language by this recognizer
        """
        return self.supported_language

    def get_version(self):
        """
        :return: The current version of this recognizer
        """
        return self.version

    def to_dict(self):
        return_dict = {"supported_entities": self.supported_entities,
                       "supported_language": self.supported_language,
                       "name": self.name,
                       "version": self.version}
        return return_dict

    @classmethod
    def from_dict(cls, entity_recognizer_dict):
        return cls(**entity_recognizer_dict)
