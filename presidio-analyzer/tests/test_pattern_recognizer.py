import re
from typing import List

import pytest

from presidio_analyzer import Pattern, RecognizerResult
from presidio_analyzer import PatternRecognizer

from tests import assert_result


class MockRecognizer(PatternRecognizer):
    def validate_result(self, pattern_text):
        return True

    def __init__(self, entity, patterns, deny_list, name, context):
        super().__init__(
            supported_entity=entity,
            name=name,
            patterns=patterns,
            deny_list=deny_list,
            context=context,
        )


def test_when_no_entity_for_pattern_recognizer_then_error():
    with pytest.raises(ValueError):
        patterns = [Pattern("p1", "someregex", 1.0), Pattern("p1", "someregex", 0.5)]
        MockRecognizer(
            entity=[], patterns=patterns, deny_list=[], name=None, context=None
        )


def test_when_deny_list_then_keywords_found():
    test_recognizer = MockRecognizer(
        patterns=[],
        entity="ENTITY_1",
        deny_list=["phone", "name"],
        context=None,
        name=None,
    )

    results = test_recognizer.analyze(
        "my phone number is 555-1234, and my name is John", ["ENTITY_1"]
    )

    assert len(results) == 2
    assert_result(results[0], "ENTITY_1", 3, 8, 1.0)
    assert_result(results[1], "ENTITY_1", 36, 40, 1.0)


def test_when_deny_list_then_keywords_not_found():
    test_recognizer = MockRecognizer(
        patterns=[],
        entity="ENTITY_1",
        deny_list=["phone", "name"],
        context=None,
        name=None,
    )

    results = test_recognizer.analyze(
        "No deny list words, though includes PII entities: 555-1234, John", ["ENTITY_1"]
    )

    assert len(results) == 0


def test_when_taken_from_dict_then_load_correctly():
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


def test_when_taken_from_dict_then_returns_instance():
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


def test_when_validation_occurs_then_analysis_explanation_is_updated():

    patterns = [Pattern(name="test_pattern", regex="([0-9]{1,9})", score=0.5)]
    mock_recognizer = MockRecognizer(
        entity="TEST",
        patterns=patterns,
        deny_list=None,
        name="MockRecognizer",
        context=None,
    )

    results: List[RecognizerResult] = mock_recognizer.analyze(
        text="Testing 1 2 3", entities=["TEST"]
    )

    assert results[0].analysis_explanation.original_score == 0.5
    assert results[0].analysis_explanation.score == 1


@pytest.mark.parametrize(
    "text, expected_len, deny_list",
    [
        ("Mr. PLUM", 1, ["Mr.", "Mrs."]),
        ("...Mr...PLUM...", 1, ["Mr.", "Mrs."]),
        ("..MMr...PLUM...", 0, ["Mr.", "Mrs."]),
        ("Mrr PLUM...", 0, ["Mr.", "Mrs."]),
        ("\\Mr.\\ PLUM...", 1, ["Mr.", "Mrs."]),
        ("\\Mr.\\ PLUM...,Mrs. Plum", 2, ["Mr.", "Mrs."]),
        ("", 0, ["Mr.", "Mrs."]),
        ("MMrrrMrs.", 0, ["Mr.", "Mrs."]),
        ("\\Mrs.", 1, ["Mr.", "Mrs."]),
        ("A B is an entity", 1, ["A B", "B C"]),
        ("A is not an entity", 0, ["A B", "B C"]),
        ("A B C", 1, ["A B", "B C"]),
        ("A B B C", 2, ["A B", "B C"]),
        ("Hi A.,.\\.B Hi", 1, ["A.,.\\.B"]),
    ],
)
def test_deny_list_non_space_separator_identified_correctly(
    text, expected_len, deny_list
):
    recognizer = PatternRecognizer(
        supported_entity="TITLE",
        name="TitlesRecognizer",
        supported_language="en",
        deny_list=deny_list,
    )

    result = recognizer.analyze(text, entities=["TITLE"])

    assert len(result) == expected_len


def test_deny_list_score_change():
    deny_list = ["Mr.", "Mrs."]
    recognizer = PatternRecognizer(
        supported_entity="TITLE",
        name="TitlesRecognizer",
        supported_language="en",
        deny_list=deny_list,
        deny_list_score=0.64,
    )

    result = recognizer.analyze(text="Mrs. Kennedy", entities=["TITLE"])
    assert result[0].score == 0.64


@pytest.mark.parametrize(
    "text,flag,expected_len",
    [("mrs. Kennedy", re.IGNORECASE, 1), ("mrs. Kennedy", re.DOTALL, 0)],
)
def test_deny_list_regex_flags(text, flag, expected_len):
    deny_list = ["Mr.", "Mrs."]
    recognizer = PatternRecognizer(
        supported_entity="TITLE",
        name="TitlesRecognizer",
        supported_language="en",
        deny_list=deny_list,
    )

    result = recognizer.analyze(text=text, entities=["TITLE"], regex_flags=flag)
    assert len(result) == expected_len


def test_empty_deny_list_raises_value_error():
    with pytest.raises(ValueError):
        PatternRecognizer(
            supported_entity="TITLE",
            name="TitlesRecognizer",
            supported_language="en",
            deny_list=[],
        )


@pytest.mark.parametrize(
    "global_flag,expected_len",
    [(re.IGNORECASE | re.MULTILINE, 2), (re.MULTILINE, 0)],
)
def test_global_regex_flag_deny_list_returns_right_result(global_flag, expected_len):
    deny_list = ["MrS", "mR"]
    text = "Mrs. smith \n\n" \
           "and Mr. Jones were sitting in the room."

    recognizer_ignore_case = PatternRecognizer(supported_entity="TITLE",
                                               name="TitlesRecognizer",
                                               deny_list=deny_list,
                                               global_regex_flags=global_flag)

    results = recognizer_ignore_case.analyze(text=text, entities=["TITLE"])
    assert len(results) == expected_len
