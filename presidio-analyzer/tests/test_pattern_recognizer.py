import pytest
import os

# https://www.datatrans.ch/showcase/test-cc-numbers
# https://www.freeformatter.com/credit-card-number-generator-validator.html
from analyzer import Pattern
from analyzer import PatternRecognizer


class MockRecognizer(PatternRecognizer):
    def __init__(self, patterns, entities, black_list, context):
        super().__init__(entities, [], patterns, black_list, context)


def test_multiple_entities_for_pattern_recognizer():
    with pytest.raises(ValueError):
        patterns = [Pattern("p1", 1.0, "someregex"), Pattern("p1", 2, "someregex")]
        MockRecognizer(["ENTITY_1", "ENTITY_2"], patterns, [], None)


def test_black_list_works():
    test_recognizer = MockRecognizer([], ["BLACK_LIST"], ["phone", "name"], None)

    results = test_recognizer.analyze_all("my phone number is 555-1234, and my name is John", ["BLACK_LIST"])

    assert len(results) == 2
    assert results[0].entity_type == "BLACK_LIST"
    assert results[0].score == 1.0
    assert results[1].entity_type == "BLACK_LIST"
    assert results[1].score == 1.0


def test_from_dict():
    json = {'supported_entities': ['ENTITY_1'],
            'supported_languages': ['en'],
            'patterns': [{'name': 'p1', 'strength': 0.5, 'pattern': '([0-9]{1,9})'}],
            'context': ['w1', 'w2', 'w3'],
            'version': 1.0}

    new_recognizer = PatternRecognizer.from_dict(json)

    results = new_recognizer.analyze_all("my phone number is 5551234", ["ENTITY_1"])

    assert len(results) == 1
    assert results[0].entity_type == "ENTITY_1"
    assert results[0].score == 0.5
    assert results[0].start == 19
    assert results[0].end == 26
