from unittest import TestCase

import pytest
import logging
from analyzer import RecognizerRegistry, PatternRecognizer, \
    EntityRecognizer, Pattern
from analyzer.recognizer_registry.recognizers_store_api \
    import RecognizerStoreApi  # noqa: F401
from analyzer.predefined_recognizers import CustomRecognizer
import time


class RecognizerStoreApiMock(RecognizerStoreApi):
    """
    A mock that acts as a recognizers store, allows to add and get recognizers
    """

    def __init__(self):
        self.latest_timestamp = 0
        self.recognizers = []
        self.times_accessed_storage = 0

    def get_latest_timestamp(self):
        return self.latest_timestamp

    def get_all_recognizers(self):
        self.times_accessed_storage = self.times_accessed_storage + 1
        return self.recognizers

    def add_custom_pattern_recognizer(self, new_recognizer,
                                      skip_timestamp_update=False):
        patterns = []
        for pat in new_recognizer.patterns:
            patterns.extend([Pattern(pat.name, pat.regex, pat.score)])
        new_custom_recognizer = CustomRecognizer(name=new_recognizer.name, entity=new_recognizer.supported_entities[0],
                                                 language=new_recognizer.supported_language,
                                                 black_list=new_recognizer.black_list,
                                                 context=new_recognizer.context,
                                                 patterns=patterns)
        self.recognizers.append(new_custom_recognizer)

        if skip_timestamp_update:
            return

        # making sure there is a time difference (when the test run so fast two
        # sequential operations are with the same timestamp
        time.sleep(1)
        self.latest_timestamp = int(time.time())

    def remove_recognizer(self, name):
        logging.info("removing recognizer " + name)
        for i in self.recognizers:
            if i.name == name:
                self.recognizers.remove(i)
        # making sure there is a time difference (when the test run so fast two
        # sequential operations are with the same timestamp
        time.sleep(1)
        self.latest_timestamp = int(time.time())


class TestRecognizerRegistry(TestCase):
    def test_dummy(self):
        assert 1 == 1

    def get_mock_pattern_recognizer(self, lang, entity, name):
        return PatternRecognizer(supported_entity=entity,
                                 supported_language=lang, name=name,
                                 patterns=[Pattern("pat", regex="REGEX",
                                                   score=1.0)])

    def get_mock_custom_recognizer(self, lang, entities, name):
        return EntityRecognizer(supported_entities=entities, name=name,
                                supported_language=lang)

    def get_mock_recognizer_registry(self):
        pattern_recognizer1 = self.get_mock_pattern_recognizer(
            "en", "PERSON", "1")
        pattern_recognizer2 = self.get_mock_pattern_recognizer(
            "de", "PERSON", "2")
        pattern_recognizer3 = self.get_mock_pattern_recognizer(
            "de", "ADDRESS", "3")
        pattern_recognizer4 = self.get_mock_pattern_recognizer(
            "he", "ADDRESS", "4")
        pattern_recognizer5 = self.get_mock_custom_recognizer(
            "he", ["PERSON", "ADDRESS"], "5")
        recognizers_store_api_mock = RecognizerStoreApiMock()
        return RecognizerRegistry(recognizers_store_api_mock,
                                  [pattern_recognizer1, pattern_recognizer2,
                                   pattern_recognizer3, pattern_recognizer4,
                                   pattern_recognizer5])

    def test_get_recognizers_all(self):
        registry = self.get_mock_recognizer_registry()
        registry.load_predefined_recognizers()
        recognizers = registry.get_recognizers()
        assert len(recognizers) == 5 + 14  # 14 predefined

    def test_get_recognizers_one_language_one_entity(self):
        registry = self.get_mock_recognizer_registry()
        recognizers = registry.get_recognizers(
            language='de', entities=["PERSON"])
        assert len(recognizers) == 1

    def test_get_recognizers_unsupported_language(self):
        with pytest.raises(ValueError):
            registry = self.get_mock_recognizer_registry()
            registry.get_recognizers(language='brrrr', entities=["PERSON"])

    def test_get_recognizers_specific_language_and_entity(self):
        registry = self.get_mock_recognizer_registry()
        recognizers = registry.get_recognizers(
            language='he', entities=["PERSON"])
        assert len(recognizers) == 1

    # Test that the the cache is working as expected, i.e iff timestamp
    # changed then need to reload from the store
    def test_cache_logic(self):
        pattern = Pattern("rocket pattern", r'\W*(rocket)\W*', 0.8)
        pattern_recognizer = PatternRecognizer("ROCKET",
                                               name="Rocket recognizer",
                                               patterns=[pattern])

        # Negative flow
        recognizers_store_api_mock = RecognizerStoreApiMock()
        recognizer_registry = RecognizerRegistry(recognizers_store_api_mock)
        custom_recognizers = recognizer_registry.get_custom_recognizers()
        # Nothing should be returned
        assert len(custom_recognizers) == 0
        # Since no timestamp was returned, then no access to storage is expected
        assert recognizers_store_api_mock.times_accessed_storage == 0

        # Add a new recognizer
        recognizers_store_api_mock.add_custom_pattern_recognizer(
            pattern_recognizer,
            skip_timestamp_update=True)

        # Since the timestamp wasn't updated the recognizers are stale from the cache
        # without the newly added one
        custom_recognizers = recognizer_registry.get_custom_recognizers()
        assert len(custom_recognizers) == 0
        # And we also didn't accessed the underlying storage
        assert recognizers_store_api_mock.times_accessed_storage == 0

        # Positive flow
        # Now do the same only this time update the timestamp so it should work properly
        recognizers_store_api_mock = RecognizerStoreApiMock()
        recognizer_registry = RecognizerRegistry(recognizers_store_api_mock)

        recognizer_registry.get_custom_recognizers()
        assert recognizers_store_api_mock.times_accessed_storage == 0
        recognizers_store_api_mock.add_custom_pattern_recognizer(
            pattern_recognizer,
            skip_timestamp_update=False)
        custom_recognizers = recognizer_registry.get_custom_recognizers()
        assert len(custom_recognizers) == 1
        # Accessed again
        assert recognizers_store_api_mock.times_accessed_storage == 1

    def test_add_pattern_recognizer(self):
        pattern = Pattern("rocket pattern", r'\W*(rocket)\W*', 0.8)
        pattern_recognizer = PatternRecognizer("ROCKET",
                                               name="Rocket recognizer",
                                               patterns=[pattern])

        # Make sure the analyzer doesn't get this entity
        recognizers_store_api_mock = RecognizerStoreApiMock()
        recognizer_registry = RecognizerRegistry(recognizers_store_api_mock)
        recognizers = recognizer_registry.get_custom_recognizers()
        assert len(recognizers) == 0

        # Add a new recognizer for the word "rocket" (case insensitive)
        recognizers_store_api_mock.add_custom_pattern_recognizer(
            pattern_recognizer)

        recognizers = recognizer_registry.get_custom_recognizers()
        assert len(recognizers) == 1
        assert recognizers[0].patterns[0].name == "rocket pattern"
        assert recognizers[0].name == "Rocket recognizer"

    def test_remove_pattern_recognizer(self):
        pattern = Pattern("spaceship pattern", r'\W*(spaceship)\W*', 0.8)
        pattern_recognizer = PatternRecognizer("SPACESHIP",
                                               name="Spaceship recognizer",
                                               patterns=[pattern])
        # Make sure the analyzer doesn't get this entity
        recognizers_store_api_mock = RecognizerStoreApiMock()
        recognizer_registry = RecognizerRegistry(recognizers_store_api_mock)

        # Expects zero custom recognizers
        recognizers = recognizer_registry.get_custom_recognizers()
        assert len(recognizers) == 0

        # Add a new recognizer for the word "rocket" (case insensitive)
        recognizers_store_api_mock.add_custom_pattern_recognizer(
            pattern_recognizer)

        # Expects one custom recognizer
        recognizers = recognizer_registry.get_custom_recognizers()
        assert len(recognizers) == 1

        # Remove recognizer
        recognizers_store_api_mock.remove_recognizer(
            "Spaceship recognizer")

        # Expects zero custom recognizers
        recognizers = recognizer_registry.get_custom_recognizers()
        assert len(recognizers) == 0
