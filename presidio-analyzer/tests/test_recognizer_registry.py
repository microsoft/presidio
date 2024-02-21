from pathlib import Path

import pytest
import regex as re

from presidio_analyzer import (
    RecognizerRegistry,
    PatternRecognizer,
    EntityRecognizer,
    Pattern,
    AnalyzerEngine,
)
from presidio_analyzer.predefined_recognizers import SpacyRecognizer


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
    # 1 custom recognizer in english + 24 predefined
    assert len(recognizers) == 1 + 24


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


def test_add_recognizer_from_dict():
    registry = RecognizerRegistry()
    recognizer = {
        "name": "Zip code Recognizer",
        "supported_language": "de",
        "patterns": [
            {
                "name": "zip code (weak)",
                "regex": "(\\b\\d{5}(?:\\-\\d{4})?\\b)",
                "score": 0.01,
            }
        ],
        "context": ["zip", "code"],
        "supported_entity": "ZIP",
    }
    registry.add_pattern_recognizer_from_dict(recognizer)

    assert len(registry.recognizers) == 1
    assert registry.recognizers[0].name == "Zip code Recognizer"


def test_recognizer_registry_add_from_yaml_file():
    this_path = Path(__file__).parent.absolute()
    test_yaml = Path(this_path, "conf/recognizers.yaml")

    registry = RecognizerRegistry()
    registry.add_recognizers_from_yaml(test_yaml)

    assert len(registry.recognizers) == 2
    zip_recogizer: PatternRecognizer = registry.get_recognizers(
        language="de", entities=["ZIP"]
    )[0]
    assert zip_recogizer.name == "Zip code Recognizer"
    assert zip_recogizer.supported_language == "de"
    assert zip_recogizer.supported_entities == ["ZIP"]
    assert len(zip_recogizer.patterns) == 1

    titles_recogizer: PatternRecognizer = registry.get_recognizers(
        language="en", entities=["TITLE"]
    )[0]
    assert titles_recogizer.name == "Titles recognizer"
    assert titles_recogizer.supported_language == "en"
    assert titles_recogizer.supported_entities == ["TITLE"]
    assert len(titles_recogizer.patterns) == 1  # deny-list turns into a pattern
    assert len(titles_recogizer.deny_list) == 6


def test_recognizer_registry_exception_missing_yaml_file():
    test_yaml = Path("missing.yaml")
    with pytest.raises(IOError):
        registry = RecognizerRegistry()
        registry.add_recognizers_from_yaml(test_yaml)


def test_recognizer_registry_exception_erroneous_yaml():
    this_path = Path(__file__).parent.absolute()
    test_yaml = Path(this_path, "conf/recognizers_error.yaml")

    with pytest.raises(TypeError):
        registry = RecognizerRegistry()
        registry.add_recognizers_from_yaml(test_yaml)


def test_predefined_pattern_recognizers_have_the_right_regex_flags():
    registry = RecognizerRegistry(global_regex_flags=re.DOTALL)
    registry.load_predefined_recognizers()
    for rec in registry.recognizers:
        if isinstance(rec, PatternRecognizer):
            assert rec.global_regex_flags == re.DOTALL


def test_recognizer_removed_and_returned_entities_are_correct():
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers()
    registry.remove_recognizer("SpacyRecognizer")
    sr = SpacyRecognizer(supported_entities=["DATE_TIME", "NRP"])
    registry.add_recognizer(sr)

    supported_entities = registry.get_supported_entities(languages=["en"])

    assert "DATE_TIME" in supported_entities
    assert "PERSON" not in supported_entities

    analyzer = AnalyzerEngine(registry=registry, supported_languages="en")

    analyzer.analyze("My name is David", language="en")
