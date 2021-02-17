import pytest

from presidio_anonymizer.entities import AnonymizerDTO, InvalidParamException


@pytest.mark.parametrize(
    # fmt: off
    "class_name",
    [
        "fpe", "hash", "mask", "redact", "replace"
    ],
    # fmt: on
)
def test_given_json_then_anonymizer_dto_is_created_properly(class_name):
    json = {
        "type": class_name,
        "param_1": "my_parameter"
    }
    anonymizer_dto = AnonymizerDTO.from_json(json)
    assert anonymizer_dto.anonymizer_class
    assert anonymizer_dto.anonymizer_class().anonymizer_name() == class_name
    assert anonymizer_dto.params == {"param_1": "my_parameter"}


@pytest.mark.parametrize(
    # fmt: off
    "class_name",
    [
        "", "Hash", "NONE"
    ],
    # fmt: on
)
def test_given_json_with_bad_anonymizer_name_then_we_fail(class_name):
    json = {
        "type": class_name,
        "param_1": "my_parameter"
    }
    with pytest.raises(InvalidParamException,
                       match=f"Invalid anonymizer class '{class_name}'."):
        AnonymizerDTO.from_json(json)
