import pytest

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.engine import AnonymizerResult
from presidio_anonymizer.entities.engine.result import OperatorResult


def test_given_anonymized_entity_then_we_parse_it_to_encrypt_result():
    anonyimzer_result = AnonymizerResult.from_operator_result(
        OperatorResult("bla", "replace", 9, 10, "PHONE_NUMBER")
    )
    assert anonyimzer_result.end == 10
    assert anonyimzer_result.start == 9
    assert anonyimzer_result.entity_type == "PHONE_NUMBER"


def test_given_valid_json_then_we_parse_it_to_encrypt_result():
    encrypt_result = AnonymizerResult.from_json({
        "start": 0,
        "end": 10,
        "entity_type": "PERSON",
    })
    assert encrypt_result.end == 10
    assert encrypt_result.start == 0
    assert encrypt_result.entity_type == "PERSON"


@pytest.mark.parametrize(
    # fmt: off
    "json,expected_result",
    [
        ({
             "end": 10,
             "key": "1111111111111111",
             "entity_type": "PERSON",
         }, "Invalid input, result must contain start"),
        ({
             "start": 0,
             "key": "1111111111111111",
             "entity_type": "PERSON",
         }, "Invalid input, result must contain end"),
        ({
             "start": 0,
             "end": 10,
             "key": "1111111111111111",
         }, "Invalid input, result must contain entity_type"),
    ],
    # fmt: on
)
def test_given_invalid_json_then_we_fail_to_parse(json, expected_result):
    with pytest.raises(InvalidParamException, match=expected_result):
        AnonymizerResult.from_json(json)
