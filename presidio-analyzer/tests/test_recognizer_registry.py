from unittest import TestCase
import pytest
from analyzer import RecognizerRegistry, PatternRecognizer, EntityRecognizer


class TestRecognizerRegistry(TestCase):

    def get_mock_pattern_recognizer(self, lang, entities):
        return PatternRecognizer(entities, lang, ["REGEX"])

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

    def test_get_supported_languages(self):
        registry = self.get_mock_recognizer_registry()
        langs = registry.get_all_supported_languages()
        assert "he" in langs
        assert "de" in langs
        assert "en" in langs

