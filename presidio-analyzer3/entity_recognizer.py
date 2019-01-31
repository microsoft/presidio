from abc import ABC, abstractmethod


class EntityRecognizer:

    def __init__(self, supported_entities, supported_languages, version):
        self.supported_entities = supported_entities
        self.supported_languages = supported_languages
        self.version = version


    @abstractmethod
    def load(self):
          pass

    @abstractmethod
    def analyze_text(self, text, entities):
        """
                This is the core method for analyzing text, assuming field_types are
                the subset of the supported field types.
                :param text: text to be analyzed
                :param entities: list of entities to be detected
                :returns list of TextMatcherResult per found result
        """

        return None

    def get_supported_entities(self):
        return self.supported_entities

    def get_supported_languages(self):
        return self.supported_languages

    def get_version(self):
        return self.version
