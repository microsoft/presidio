from tests import Pattern
from tests import PatternRecognizer
import pytest
import os

# https://www.datatrans.ch/showcase/test-cc-numbers
# https://www.freeformatter.com/credit-card-number-generator-validator.html


class TestRecognizer(PatternRecognizer):
    def __init__(self, patterns, entities, black_list, context):

        super().__init__(entities, [], patterns, black_list, context)


def test_multiple_entities_for_pattern_recognizer():
    with pytest.raises(ValueError):
        patterns = [Pattern("p1", 1.0, "someregex"), Pattern("p1", 2, "someregex")]
        TestRecognizer(["ENTITY_1", "ENTITY_2"], patterns, [], None)


def test_black_list_works():
    test_recognizer = TestRecognizer([], ["BLACK_LIST"], ["phone", "name"], None)

    results = test_recognizer.analyze_all("my phone number is 555-1234, and my name is John", ["BLAcK_LIST"])

    assert len(results) == 2
    assert results[0].entity_type == "BLACK_LIST"
    assert results[0].score == 1.0
    assert results[1].entity_type == "BLACK_LIST"
    assert results[1].score == 1.0
