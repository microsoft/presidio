from unittest import TestCase

import pytest

from analyzer import RecognizerRegistry, PatternRecognizer, EntityRecognizer, Pattern


class TestRecognizerRegistry(TestCase):

    def get_mock_pattern_recognizer(self, lang, entities):
        return PatternRecognizer(supported_entities=entities,
                                 supported_language=lang,
                                 patterns=[Pattern("pat", pattern="REGEX", strength=1.0)])

    def get_mock_cusom_recognizer(self, lang, entities):
        return EntityRecognizer(entities, lang)

    def get_mock_recognizer_registry(self):
        pattern_recognizer1 = self.get_mock_pattern_recognizer("en", ["PERSON"])
        pattern_recognizer2 = self.get_mock_pattern_recognizer("de", ["PERSON"])
        pattern_recognizer3 = self.get_mock_pattern_recognizer("de", ["ADDRESS"])
        pattern_recognizer4 = self.get_mock_pattern_recognizer("he", ["ADDRESS"])
        pattern_recognizer5 = self.get_mock_cusom_recognizer("he", ["PERSON", "ADDRESS"])
        return RecognizerRegistry([pattern_recognizer1, pattern_recognizer2,
                                   pattern_recognizer3, pattern_recognizer4,
                                   pattern_recognizer5])

    def test_get_recognizers_all(self):
        registry = self.get_mock_recognizer_registry()
        recognizers = registry.get_recognizers()
        assert len(recognizers) == 5

    def test_get_recognizers_one_language_one_entity(self):
        registry = self.get_mock_recognizer_registry()
        recognizers = registry.get_recognizers(language='de', entities=["PERSON"])
        assert len(recognizers) == 1

    def test_get_recognizers_unsupported_language(self):
        with pytest.raises(ValueError):
            registry = self.get_mock_recognizer_registry()
            registry.get_recognizers(language='brrrr', entities=["PERSON"])

    def test_get_recognizers_specific_language_and_entity(self):
        registry = self.get_mock_recognizer_registry()
        recognizers = registry.get_recognizers(language='he', entities=["PERSON"])
        assert len(recognizers) == 1

    def test_load_pattern_recognizer_from_dict(self):
        pattern_recognizer = self.get_mock_pattern_recognizer("ar", ["ENTITY"])
        registry = self.get_mock_recognizer_registry()
        registry.add_pattern_recognizer_from_dict(pattern_recognizer.to_dict())

        recognizers = registry.get_recognizers(entities=["ENTITY"], language="ar")

        assert recognizers[0].to_dict() == pattern_recognizer.to_dict()

    def test_load_pattern_recognizer_from_dict_already_defined_throws_exception(self):
        pattern_recognizer1 = self.get_mock_pattern_recognizer("ar", ["ENTITY"])
        pattern_recognizer1.name = "MyRecognizer"
        registry = self.get_mock_recognizer_registry()
        registry.add_pattern_recognizer_from_dict(pattern_recognizer1.to_dict())

        pattern_recognizer2 = self.get_mock_pattern_recognizer("em", ["ENTITY3"])
        pattern_recognizer2.name = "MyRecognizer"
        with pytest.raises(ValueError):
            registry.add_pattern_recognizer_from_dict(pattern_recognizer2.to_dict())

    def test_remove_pattern_recognizer_not_found_exception(self):
        pattern_recognizer1 = self.get_mock_pattern_recognizer("ar", ["ENTITY"])
        pattern_recognizer1.name = "MyRecognizer"
        registry = self.get_mock_recognizer_registry()
        registry.add_pattern_recognizer_from_dict(pattern_recognizer1.to_dict())

        with pytest.raises(ValueError):
            registry.remove_recognizer("NumeroUnoRecognizer")

    def test_remove_pattern_recognizer_removed(self):
        pattern_recognizer1 = self.get_mock_pattern_recognizer("ar", ["ENTITY"])
        pattern_recognizer1.name = "MyRecognizer"
        registry = self.get_mock_recognizer_registry()
        registry.add_pattern_recognizer_from_dict(pattern_recognizer1.to_dict())

        assert len(registry.recognizers) == 6


        registry.remove_recognizer("MyRecognizer")

        assert len(registry.recognizers) == 5

        for recognizer in registry.recognizers:
            if recognizer.name == "MyRecognizer":
                assert False

        assert True
