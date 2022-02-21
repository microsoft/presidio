import pytest

from presidio_analyzer import (
    RecognizerRegistry,
    PatternRecognizer,
    EntityRecognizer,
    Pattern,
)


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
    return RecognizerRegistry(
        [
            pattern_recognizer1,
            pattern_recognizer2,
            pattern_recognizer3,
            pattern_recognizer4,
            pattern_recognizer5,
        ],
    )


def test_when_get_recognizers_then_all_recognizers_returned(mock_recognizer_registry):
    registry = mock_recognizer_registry
    registry.load_predefined_recognizers()
    recognizers = registry.get_recognizers(language="en", all_fields=True)
    # 1 custom recognizer in english + 21 predefined
    assert len(recognizers) == 1 + 21


def test_when_get_recognizers_then_return_all_fields(mock_recognizer_registry):
    registry = mock_recognizer_registry
    recognizers = registry.get_recognizers(language="de", all_fields=True)
    assert len(recognizers) == 2


def test_when_get_recognizers_one_language_then_return_one_entity(
    mock_recognizer_registry,
):
    registry = mock_recognizer_registry
    recognizers = registry.get_recognizers(language="de", entities=["PERSON"])
    assert len(recognizers) == 1


def test_when_get_recognizers_unsupported_language_then_return(
    mock_recognizer_registry,
):
    with pytest.raises(ValueError):
        registry = mock_recognizer_registry
        registry.get_recognizers(language="brrrr", entities=["PERSON"])


def test_when_get_recognizers_specific_language_and_entity_then_return_one_result(
    mock_recognizer_registry,
):
    registry = mock_recognizer_registry
    recognizers = registry.get_recognizers(language="he", entities=["PERSON"])
    assert len(recognizers) == 1


def test_when_multiple_entities_from_same_recognizer_only_one_is_returned():
    registry = RecognizerRegistry()

    recognizer_supporting_two_ents = EntityRecognizer(
        supported_entities=["A", "B"], name="MyReco"
    )
    registry.add_recognizer(recognizer_supporting_two_ents)
    recognizers = registry.get_recognizers(
        language="en", entities=["A", "B"], all_fields=False
    )

    assert len(recognizers) == 1
    assert recognizers[0].name == "MyReco"


def test_when_add_pattern_recognizer_then_item_added():
    pattern = Pattern("rocket pattern", r"\W*(rocket)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "ROCKET", name="Rocket recognizer", patterns=[pattern]
    )

    # Create an empty recognizer registry
    recognizer_registry = RecognizerRegistry(recognizers=[])
    assert len(recognizer_registry.recognizers) == 0

    # Add a new recognizer for the word "rocket" (case insensitive)
    recognizer_registry.add_recognizer(pattern_recognizer)

    assert len(recognizer_registry.recognizers) == 1
    assert recognizer_registry.recognizers[0].patterns[0].name == "rocket pattern"
    assert recognizer_registry.recognizers[0].name == "Rocket recognizer"


def test_when_remove_pattern_recognizer_then_item_removed():
    pattern = Pattern("spaceship pattern", r"\W*(spaceship)\W*", 0.8)
    pattern_recognizer = PatternRecognizer(
        "SPACESHIP", name="Spaceship recognizer", patterns=[pattern]
    )
    # Create an empty recognizer registry
    recognizer_registry = RecognizerRegistry(recognizers=[])
    assert len(recognizer_registry.recognizers) == 0

    # Add a new recognizer for the word "rocket" (case insensitive)
    recognizer_registry.add_recognizer(pattern_recognizer)

    # Expects one custom recognizer
    assert len(recognizer_registry.recognizers) == 1

    # Remove recognizer
    recognizer_registry.remove_recognizer("Spaceship recognizer")

    # Expects zero custom recognizers
    assert len(recognizer_registry.recognizers) == 0
