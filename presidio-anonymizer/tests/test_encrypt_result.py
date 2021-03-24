import pytest

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.engine import EncryptResult
from presidio_anonymizer.entities.engine.result import AnonymizedEntity


def test_given_anonymized_entity_then_we_parse_it_to_encrypt_result():
    encrypt_result = EncryptResult.from_anonymized_entity(
        "1111111111111111",
        AnonymizedEntity(9, 10, "DSKMDEWO#*!)*&E!#KNDMLNC", "PHONE_NUMBER", "bla")
    )
    assert encrypt_result.end == 10
    assert encrypt_result.start == 9
    assert encrypt_result.key == "1111111111111111"
    assert encrypt_result.entity_type == "PHONE_NUMBER"


def test_given_valid_json_then_we_parse_it_to_encrypt_result():
    encrypt_result = EncryptResult.from_json({
        "start": 0,
        "end": 10,
        "key": "1111111111111111",
        "entity_type": "PERSON",
    })
    assert encrypt_result.end == 10
    assert encrypt_result.start == 0
    assert encrypt_result.key == "1111111111111111"
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
             "entity_type": "PERSON",
         }, "Invalid input, decrypt entity must contain key"),
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
        EncryptResult.from_json(json)
