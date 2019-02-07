from unittest import TestCase

import pytest

# https://www.datatrans.ch/showcase/test-cc-numbers
# https://www.freeformatter.com/credit-card-number-generator-validator.html
from analyzer import Pattern
from analyzer import PatternRecognizer


class MockRecognizer(PatternRecognizer):
    def __init__(self, patterns, entities, black_list, context):
        super().__init__(entities, None, patterns, black_list, context)


class TestPatternRecognizer(TestCase):

    def test_multiple_entities_for_pattern_recognizer(self):
        with pytest.raises(ValueError):
            patterns = [Pattern("p1", "someregex", 1.0), Pattern("p1", "someregex", 0.5)]
            MockRecognizer(["ENTITY_1", "ENTITY_2"], patterns, [], None)

    def test_black_list_works(self):
        test_recognizer = MockRecognizer([], ["ENTITY_1"], ["phone", "name"], None)

        results = test_recognizer.analyze("my phone number is 555-1234, and my name is John", ["ENTITY_1"])

        assert len(results) == 2
        assert results[0].entity_type == "ENTITY_1"
        assert results[0].score == 1.0
        assert results[0].start == 3
        assert results[0].end == 8

        assert results[1].entity_type == "ENTITY_1"
        assert results[1].score == 1.0
        assert results[1].start == 36
        assert results[1].end == 40

    def test_from_dict(self):
        json = {'supported_entities': ['ENTITY_1'],
                'supported_language': 'en',
                'patterns': [{'name': 'p1', 'strength': 0.5, 'pattern': '([0-9]{1,9})'}],
                'context': ['w1', 'w2', 'w3'],
                'version': "1.0"}

        new_recognizer = PatternRecognizer.from_dict(json)
        assert new_recognizer.supported_entities == ['ENTITY_1']
        assert new_recognizer.supported_language == 'en'
        assert new_recognizer.patterns[0].name == 'p1'
        assert new_recognizer.patterns[0].strength == 0.5
        assert new_recognizer.patterns[0].pattern == '([0-9]{1,9})'
        assert new_recognizer.context == ['w1','w2','w3']
        assert new_recognizer.version == "1.0"


    def test_from_dict_returns_instance(self):
        pattern1_dict = {'name': 'p1', 'strength': 0.5, 'pattern': '([0-9]{1,9})'}
        pattern2_dict = {'name': 'p2', 'strength': 0.8, 'pattern': '([0-9]{1,9})'}

        ent_rec_dict = {"supported_entities": ["A"],
                        "supported_language": "he",
                        "patterns": [pattern1_dict, pattern2_dict]
                        }
        pattern_recognizer = PatternRecognizer.from_dict(ent_rec_dict)

        assert pattern_recognizer.supported_entities == ["A"]
        assert pattern_recognizer.supported_language == "he"
        assert pattern_recognizer.version == "0.0.1"

        assert pattern_recognizer.patterns[0].name == "p1"
        assert pattern_recognizer.patterns[0].strength == 0.5
        assert pattern_recognizer.patterns[0].pattern == '([0-9]{1,9})'

        assert pattern_recognizer.patterns[1].name == "p2"
        assert pattern_recognizer.patterns[1].strength == 0.8
        assert pattern_recognizer.patterns[1].pattern == '([0-9]{1,9})'
