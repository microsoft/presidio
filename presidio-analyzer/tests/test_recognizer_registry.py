import hashlib
import logging

import pytest

from presidio_analyzer import (
    RecognizerRegistry,
    PatternRecognizer,
    EntityRecognizer,
    Pattern,
)
from presidio_analyzer.recognizer_registry.recognizers_store_api import (
    RecognizerStoreApi,
)  # noqa: F401


class RecognizerStoreApiMock(RecognizerStoreApi):
    """
    A mock that acts as a recognizers store, allows to add and get recognizers
    """

    def __init__(self):
        self.latest_hash = None
        self.recognizers = []
        self.times_accessed_storage = 0

    def get_latest_hash(self):
        return self.latest_hash

    def get_all_recognizers(self):
        self.times_accessed_storage = self.times_accessed_storage + 1
        return self.recognizers

    def add_custom_pattern_recognizer(self, new_recognizer, skip_hash_update=False):
        patterns = []
        for pat in new_recognizer.patterns:
            patterns.extend([Pattern(pat.name, pat.regex, pat.score)])
        new_custom_recognizer = PatternRecognizer(
            name=new_recognizer.name,
            supported_entity=new_recognizer.supported_entities[0],
            supported_language=new_recognizer.supported_language,
            black_list=new_recognizer.black_list,
            context=new_recognizer.context,
            patterns=patterns,
        )
        self.recognizers.append(new_custom_recognizer)

        if skip_hash_update:
            return

        m = hashlib.md5()
        for recognizer in self.recognizers:
            m.update(recognizer.name.encode("utf-8"))
        self.latest_hash = m.digest()

    def remove_recognizer(self, name):
        logging.info("removing recognizer %s", name)
        for i in self.recognizers:
            if i.name == name:
                self.recognizers.remove(i)
        m = hashlib.md5()
        for recognizer in self.recognizers:
            m.update(recognizer.name.encode("utf-8"))
        self.latest_hash = m.digest()


@pytest.fixture(scope="module")
def request_id():
    return "UT"


def create_mock_pattern_recognizer(lang, entity, name):
    return PatternRecognizer(
        supported_entity=entity,
        supported_language=lang,
        name=name,
        patterns=[Pattern("pat", regex="REGEX", score=1.0)],
    )


def create_mock_custom_recognizer(lang, entities, name):
    return EntityRecognizer(
        supported_entities=entities, name=name, supported_language=lang
    )


@pytest.fixture(scope="function")
def mock_recognizer_registry():
    pattern_recognizer1 = create_mock_pattern_recognizer("en", "PERSON", "1")
    pattern_recognizer2 = create_mock_pattern_recognizer("de", "PERSON", "2")
    pattern_recognizer3 = create_mock_pattern_recognizer("de", "ADDRESS", "3")
    pattern_recognizer4 = create_mock_pattern_recognizer("he", "ADDRESS", "4")
    pattern_recognizer5 = create_mock_custom_recognizer(
        "he", ["PERSON", "ADDRESS"], "5"
    )
    recognizers_store_api_mock = RecognizerStoreApiMock()
    return RecognizerRegistry(
        recognizers_store_api_mock,
        [
            pattern_recognizer1,
            pattern_recognizer2,
            pattern_recognizer3,
            pattern_recognizer4,
            pattern_recognizer5,
        ],
    )


def test_get_recognizers_all(mock_recognizer_registry):
    registry = mock_recognizer_registry
    registry.load_predefined_recognizers()
    recognizers = registry.get_recognizers(language="en", all_fields=True)
    # 1 custom recognizer in english + 15 predefined
    assert len(recognizers) == 1 + 15


def test_get_recognizers_all_fields(mock_recognizer_registry):
    registry = mock_recognizer_registry
    recognizers = registry.get_recognizers(language="de", all_fields=True)
    assert len(recognizers) == 2


def test_get_recognizers_one_language_one_entity(mock_recognizer_registry):
    registry = mock_recognizer_registry
    recognizers = registry.get_recognizers(language="de", entities=["PERSON"])
    assert len(recognizers) == 1


def test_get_recognizers_unsupported_language(mock_recognizer_registry):
    with pytest.raises(ValueError):
        registry = mock_recognizer_registry
        registry.get_recognizers(language="brrrr", entities=["PERSON"])


def test_get_recognizers_specific_language_and_entity(mock_recognizer_registry):
    registry = mock_recognizer_registry
    recognizers = registry.get_recognizers(language="he", entities=["PERSON"])
    assert len(recognizers) == 1


# Test that the the cache is working as expected, i.e iff hash
# changed then need to reload from the store
def test_cache_logic():
    pattern = Pattern("rocket pattern", r"\W*(rocket)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "ROCKET", name="Rocket recognizer", patterns=[pattern]
    )

    # Negative flow
    recognizers_store_api_mock = RecognizerStoreApiMock()
    recognizer_registry = RecognizerRegistry(recognizers_store_api_mock)
    custom_recognizers = recognizer_registry.get_custom_recognizers()
    # Nothing should be returned
    assert len(custom_recognizers) == 0
    # Since no hash was returned, then no access to storage is expected
    assert recognizers_store_api_mock.times_accessed_storage == 0

    # Add a new recognizer
    recognizers_store_api_mock.add_custom_pattern_recognizer(
        pattern_recognizer, skip_hash_update=True
    )

    # Since the hash wasn't updated the recognizers are stale from the cache
    # without the newly added one
    custom_recognizers = recognizer_registry.get_custom_recognizers()
    assert len(custom_recognizers) == 0
    # And we also didn't accessed the underlying storage
    assert recognizers_store_api_mock.times_accessed_storage == 0

    # Positive flow
    # Now do the same only this time update the hash so it should work properly
    recognizers_store_api_mock = RecognizerStoreApiMock()
    recognizer_registry = RecognizerRegistry(recognizers_store_api_mock)

    recognizer_registry.get_custom_recognizers()
    assert recognizers_store_api_mock.times_accessed_storage == 0
    recognizers_store_api_mock.add_custom_pattern_recognizer(
        pattern_recognizer, skip_hash_update=False
    )
    custom_recognizers = recognizer_registry.get_custom_recognizers()
    assert len(custom_recognizers) == 1
    # Accessed again
    assert recognizers_store_api_mock.times_accessed_storage == 1


def test_add_pattern_recognizer():
    pattern = Pattern("rocket pattern", r"\W*(rocket)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "ROCKET", name="Rocket recognizer", patterns=[pattern]
    )

    # Make sure the analyzer doesn't get this entity
    recognizers_store_api_mock = RecognizerStoreApiMock()
    recognizer_registry = RecognizerRegistry(recognizers_store_api_mock)
    recognizers = recognizer_registry.get_custom_recognizers()
    assert len(recognizers) == 0

    # Add a new recognizer for the word "rocket" (case insensitive)
    recognizers_store_api_mock.add_custom_pattern_recognizer(pattern_recognizer)

    recognizers = recognizer_registry.get_custom_recognizers()
    assert len(recognizers) == 1
    assert recognizers[0].patterns[0].name == "rocket pattern"
    assert recognizers[0].name == "Rocket recognizer"


def test_remove_pattern_recognizer():
    pattern = Pattern("spaceship pattern", r"\W*(spaceship)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "SPACESHIP", name="Spaceship recognizer", patterns=[pattern]
    )
    # Make sure the analyzer doesn't get this entity
    recognizers_store_api_mock = RecognizerStoreApiMock()
    recognizer_registry = RecognizerRegistry(recognizers_store_api_mock)

    # Expects zero custom recognizers
    recognizers = recognizer_registry.get_custom_recognizers()
    assert len(recognizers) == 0

    # Add a new recognizer for the word "rocket" (case insensitive)
    recognizers_store_api_mock.add_custom_pattern_recognizer(pattern_recognizer)

    # Expects one custom recognizer
    recognizers = recognizer_registry.get_custom_recognizers()
    assert len(recognizers) == 1

    # Remove recognizer
    recognizers_store_api_mock.remove_recognizer("Spaceship recognizer")

    # Expects zero custom recognizers
    recognizers = recognizer_registry.get_custom_recognizers()
    assert len(recognizers) == 0
