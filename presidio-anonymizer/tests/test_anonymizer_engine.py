from typing import Dict, List

import pytest

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import (
    AnonymizerConfig,
    InvalidParamException,
    RecognizerResult,
)
from presidio_anonymizer.entities.manipulator.manipulated_result_item import \
    ManipulatedResultItem
from presidio_anonymizer.entities.manipulator.manipulator_result import \
    ManipulatorResult
from presidio_anonymizer.entities.manipulator.text_manipulation_item import \
    TextManipulationItem


def test_given_request_anonymizers_return_list():
    engine = AnonymizerEngine()
    expected_list = ["hash", "mask", "redact", "replace", "encrypt"]
    anon_list = engine.get_anonymizers()

    assert anon_list == expected_list


def test_given_empty_text_to_engine_then_we_fail():
    engine = AnonymizerEngine()
    analyzer_result = RecognizerResult("SSN", 0, 1, 0.5)
    with pytest.raises(
            InvalidParamException, match="Invalid input, text can not be empty"
    ):
        engine.anonymize("", [analyzer_result], {})


def test_given_empty_analyzers_list_then_we_get_same_text_back():
    engine = AnonymizerEngine()
    text = "one two three"
    assert engine.anonymize(text, [], {}).text == text


def test_given_empty_anonymziers_list_then_we_fall_to_default():
    engine = AnonymizerEngine()
    text = "please REPLACE ME."
    analyzer_result = RecognizerResult("SSN", 7, 17, 0.8)
    result = engine.anonymize(text, [analyzer_result], {}).text
    assert result == "please <SSN>."


def test_given_none_as_anonymziers_list_then_we_fall_to_default():
    engine = AnonymizerEngine()
    text = "please REPLACE ME."
    analyzer_result = RecognizerResult("SSN", 7, 17, 0.8)
    result = engine.anonymize(text, [analyzer_result]).text
    assert result == "please <SSN>."


def test_given_default_anonymizer_then_we_use_it():
    engine = AnonymizerEngine()
    text = "please REPLACE ME."
    analyzer_result = RecognizerResult("SSN", 7, 17, 0.8)
    anonymizer_config = AnonymizerConfig("replace", {"new_value": "and thank you"})
    result = engine.anonymize(
        text, [analyzer_result], {"DEFAULT": anonymizer_config}
    ).text
    assert result == "please and thank you."


def test_given_specific_anonymizer_then_we_use_it():
    engine = AnonymizerEngine()
    text = "please REPLACE ME."
    analyzer_result = RecognizerResult("SSN", 7, 17, 0.8)
    anonymizer_config = AnonymizerConfig("replace", {"new_value": "and thank you"})
    ssn_anonymizer_config = AnonymizerConfig("redact", {})
    result = engine.anonymize(
        text,
        [analyzer_result],
        {"DEFAULT": anonymizer_config, "SSN": ssn_anonymizer_config},
    ).text
    assert result == "please ."


@pytest.mark.parametrize(
    # fmt: off
    "original_text,start,end",
    [
        ("hello world", 5, 12),
        ("hello world", 12, 16),
    ],
    # fmt: on
)
def test_given_analyzer_result_with_an_incorrect_text_positions_then_we_fail(
        original_text, start, end
):
    engine = AnonymizerEngine()
    analyzer_result = RecognizerResult("type", start, end, 0.5)
    err_msg = (
        f"Invalid analyzer result, start: {start} and end: "
        f"{end}, while text length is only 11."
    )
    with pytest.raises(InvalidParamException, match=err_msg):
        engine.anonymize(original_text, [analyzer_result], {})


def test_given_several_anonymizers_then_we_use_the_correct_one():
    analyzer_results = RecognizerResult.handle_analyzer_results_json(
        [{"start": 48, "end": 57, "score": 0.95, "entity_type": "PHONE_NUMBER"},
         {"start": 24, "end": 32, "score": 0.6, "entity_type": "FULL_NAME"},
         {"start": 24, "end": 28, "score": 0.9, "entity_type": "FIRST_NAME"},
         {"start": 29, "end": 32, "score": 0.6, "entity_type": "LAST_NAME"},
         {"start": 24, "end": 30, "score": 0.8, "entity_type": "NAME"},
         {"start": 18, "end": 32, "score": 0.8, "entity_type": "BLA"},
         {"start": 23, "end": 35, "score": 0.8, "entity_type": "BLA"},
         {"start": 28, "end": 36, "score": 0.8, "entity_type": "BLA"}],
    )
    anonymizer_config = AnonymizerConfig("replace", {})
    anonymizer_config.anonymizer_class = MockAnonymizer
    engine = AnonymizerEngine()
    engine.text_manipulator = MockTextManipulator()
    result = engine.anonymize(
            "hello world, my name is Jane Doe. My number is: 034453334",
            analyzer_results,
            {"DEFAULT": anonymizer_config}
        )

    assert result.text == "Number: I am your new text!"
    assert len(result.items) == 1
    assert result.items[0].anonymizer == "hash"
    assert result.items[0].entity_type == "type"
    assert result.items[0].start == 0
    assert result.items[0].end == 35
    assert result.items[0].anonymized_text == "text"


class MockTextManipulator:
    def manipulate_text(self, text: str,
                        manipulations: List[TextManipulationItem]) -> ManipulatorResult:
        assert text == "hello world, my name is Jane Doe. My number is: 034453334"
        assert len(manipulations) == 4
        expected = [RecognizerResult(start=48, end=57, score=0.95, entity_type="PHONE_NUMBER"),
             RecognizerResult(start=18, end=32, score=0.8, entity_type="BLA"),
             RecognizerResult(start=23, end=35, score=0.8, entity_type="BLA"),
             RecognizerResult(start=28, end=36, score=0.8, entity_type="BLA")]
        assert all(elem in manipulations for elem in expected)
        return ManipulatorResult("Number: I am your new text!", [ManipulatedResultItem("hash", "type", 0, 35, "text")])


class MockAnonymizer:
    def operate(self, text: str, params: Dict = None):
        return "I am your new text!"

    def validate(self, params):
        pass

    def operator_name(self):
        return "name"
