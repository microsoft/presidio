import pytest

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import AnonymizerConfig, InvalidParamException, \
    AnalyzerResult


def test_given_request_anonymizers_return_list():
    engine = AnonymizerEngine()
    expected_list = ["fpe", "hash", "mask", "redact", "replace"]
    anon_list = engine.anonymizers()

    assert anon_list == expected_list


def test_given_empty_text_to_engine_then_we_fail():
    engine = AnonymizerEngine()
    analyzer_result = AnalyzerResult("SSN", 0, 1, 0.5)
    with pytest.raises(InvalidParamException,
                       match="Invalid input, text can not be empty"):
        engine.anonymize("", [analyzer_result], {})


def test_given_empty_analyzers_list_then_we_get_same_text_back():
    engine = AnonymizerEngine()
    text = "one two three"
    assert engine.anonymize(text, [], {}) == text


def test_given_empty_anonymziers_list_then_we_fall_to_default():
    engine = AnonymizerEngine()
    text = "please REPLACE ME."
    analyzer_result = AnalyzerResult("SSN", 7, 17, 0.8)
    result = engine.anonymize(text, [analyzer_result], {})
    assert result == "please <SSN>."


def test_given_none_as_anonymziers_list_then_we_fall_to_default():
    engine = AnonymizerEngine()
    text = "please REPLACE ME."
    analyzer_result = AnalyzerResult("SSN", 7, 17, 0.8)
    result = engine.anonymize(text, [analyzer_result])
    assert result == "please <SSN>."


def test_given_default_anonymizer_then_we_use_it():
    engine = AnonymizerEngine()
    text = "please REPLACE ME."
    analyzer_result = AnalyzerResult("SSN", 7, 17, 0.8)
    anonymizer_config = AnonymizerConfig("replace", {"new_value": "and thank you"})
    result = engine.anonymize(text, [analyzer_result], {"DEFAULT": anonymizer_config})
    assert result == "please and thank you."


def test_given_specific_anonymizer_then_we_use_it():
    engine = AnonymizerEngine()
    text = "please REPLACE ME."
    analyzer_result = AnalyzerResult("SSN", 7, 17, 0.8)
    anonymizer_config = AnonymizerConfig("replace", {"new_value": "and thank you"})
    ssn_anonymizer_config = AnonymizerConfig("redact", {})
    result = engine.anonymize(text, [analyzer_result], {"DEFAULT": anonymizer_config,
                                                        "SSN": ssn_anonymizer_config})
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
        original_text, start, end):
    engine = AnonymizerEngine()
    analyzer_result = AnalyzerResult("type", start, end, 0.5)
    err_msg = f"Invalid analyzer result, start: {start} and end: " \
              f"{end}, while text length is only 11."
    with pytest.raises(InvalidParamException, match=err_msg):
        engine.anonymize(original_text, [analyzer_result], {})


def test_given_several_anonymizers_then_we_use_the_correct_one():
    analyzer_result = AnalyzerResult.from_json(
        {"score": 0.5, "entity_type": "PHONE_NUMBER", "start": 8, "end": 18}
    )
    anonymizer_config = AnonymizerConfig("replace", {})
    anonymizer_config.anonymizer_class = MockAnonymizer
    text = AnonymizerEngine().anonymize("Number: 0554555556", [analyzer_result],
                                        {"PHONE_NUMBER": anonymizer_config})
    assert text == "Number: I am your new text!"


class MockAnonymizer:
    def anonymize(self, text: str, params: dict = None):
        return "I am your new text!"

    def validate(self, params):
        pass
