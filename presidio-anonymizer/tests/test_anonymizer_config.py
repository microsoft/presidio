import pytest

from presidio_anonymizer.entities.engine import AnonymizeConfig


@pytest.mark.parametrize(
    # fmt: off
    "class_name",
    [
        "hash", "mask", "redact", "replace"
    ],
    # fmt: on
)
def test_given_json_then_anonymizer_config_is_created_properly(class_name):
    json = {"type": class_name, "param_1": "my_parameter"}
    anonymizer_config = AnonymizeConfig.from_json(json)
    assert anonymizer_config.operator_name == class_name
    assert anonymizer_config.params == {"param_1": "my_parameter"}
