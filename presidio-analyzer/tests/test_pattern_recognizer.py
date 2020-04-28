import pytest

# https://www.datatrans.ch/showcase/test-cc-numbers
# https://www.freeformatter.com/credit-card-number-generator-validator.html
from tests import assert_result
from presidio_analyzer import Pattern
from presidio_analyzer import PatternRecognizer


class MockRecognizer(PatternRecognizer):
    def validate_result(self, pattern_text):
        return True

    def __init__(self, entity, patterns, black_list, name, context):
        super().__init__(
            supported_entity=entity,
            name=name,
            patterns=patterns,
            black_list=black_list,
            context=context,
        )


def test_no_entity_for_pattern_recognizer():
    with pytest.raises(ValueError):
        patterns = [Pattern("p1", "someregex", 1.0), Pattern("p1", "someregex", 0.5)]
        MockRecognizer(
            entity=[], patterns=patterns, black_list=[], name=None, context=None
        )


def test_black_list_keywords_found():
    test_recognizer = MockRecognizer(
        patterns=[],
        entity="ENTITY_1",
        black_list=["phone", "name"],
        context=None,
        name=None,
    )

    results = test_recognizer.analyze(
        "my phone number is 555-1234, and my name is John", ["ENTITY_1"]
    )

    assert len(results) == 2
    assert_result(results[0], "ENTITY_1", 3, 8, 1.0)
    assert_result(results[1], "ENTITY_1", 36, 40, 1.0)


def test_black_list_keywords_not_found():
    test_recognizer = MockRecognizer(
        patterns=[],
        entity="ENTITY_1",
        black_list=["phone", "name"],
        context=None,
        name=None,
    )

    results = test_recognizer.analyze(
        "No blacklist words, though includes PII entities: 555-1234, John", ["ENTITY_1"]
    )

    assert len(results) == 0


def test_from_dict():
    json = {
        "supported_entity": "ENTITY_1",
        "supported_language": "en",
        "patterns": [{"name": "p1", "score": 0.5, "regex": "([0-9]{1,9})"}],
        "context": ["w1", "w2", "w3"],
        "version": "1.0",
    }

    new_recognizer = PatternRecognizer.from_dict(json)
    # consider refactoring assertions
    assert new_recognizer.supported_entities == ["ENTITY_1"]
    assert new_recognizer.supported_language == "en"
    assert new_recognizer.patterns[0].name == "p1"
    assert new_recognizer.patterns[0].score == 0.5
    assert new_recognizer.patterns[0].regex == "([0-9]{1,9})"
    assert new_recognizer.context == ["w1", "w2", "w3"]
    assert new_recognizer.version == "1.0"


def test_from_dict_returns_instance():
    pattern1_dict = {"name": "p1", "score": 0.5, "regex": "([0-9]{1,9})"}
    pattern2_dict = {"name": "p2", "score": 0.8, "regex": "([0-9]{1,9})"}

    ent_rec_dict = {
        "supported_entity": "A",
        "supported_language": "he",
        "patterns": [pattern1_dict, pattern2_dict],
    }
    pattern_recognizer = PatternRecognizer.from_dict(ent_rec_dict)

    assert pattern_recognizer.supported_entities == ["A"]
    assert pattern_recognizer.supported_language == "he"
    assert pattern_recognizer.version == "0.0.1"

    assert pattern_recognizer.patterns[0].name == "p1"
    assert pattern_recognizer.patterns[0].score == 0.5
    assert pattern_recognizer.patterns[0].regex == "([0-9]{1,9})"

    assert pattern_recognizer.patterns[1].name == "p2"
    assert pattern_recognizer.patterns[1].score == 0.8
    assert pattern_recognizer.patterns[1].regex == "([0-9]{1,9})"
