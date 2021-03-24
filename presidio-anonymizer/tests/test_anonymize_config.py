import pytest

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.engine import AnonymizerConfig, OperatorConfig
from presidio_anonymizer.operators import OperatorType


def test_given_valid_json_then_we_parse_it_to_anonymize_config():
    anonymize_config = AnonymizerConfig.from_json({
        "type": "mask",
        "masking_char": "*",
        "chars_to_mask": 4,
        "from_end": True
    })
    assert anonymize_config.operator_type == OperatorType.Anonymize
    assert anonymize_config.operator_name == "mask"
    assert anonymize_config.params == {"masking_char": "*", "chars_to_mask": 4,
                                       "from_end": True}


def test_given_invalid_json_then_we_fail_to_parse_it_to_anonymize_config():
    expected_error = "Invalid input, config must contain operator_name"
    with pytest.raises(InvalidParamException, match=expected_error):
        AnonymizerConfig.from_json({
            "masking_char": "*",
            "chars_to_mask": 4,
            "from_end": True
        })


def test_creating_operator_md_without_operator_type_then_we_fail():
    expected_error = "Invalid input, invalid operator type 4"
    with pytest.raises(InvalidParamException, match=expected_error):
        OperatorConfig(4, {}, "anonymizer_name")


def test_given_two_identical_entities_then_we_verify_they_are_equal():
    one = AnonymizerConfig("name", {"key", "key"})
    two = AnonymizerConfig("name", {"key", "key"})
    assert one == two


@pytest.mark.parametrize(
    # fmt: off
    "anonymizer_config",
    [
        AnonymizerConfig("name1", {"key", "key"}),
        AnonymizerConfig("name1", {}),
    ],
    # fmt: on
)
def test_given_two_different_entities_then_we_verify_they_are_equal(anonymizer_config):
    one = AnonymizerConfig("name", {"key", "key"})
    assert one != anonymizer_config


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
    anonymizer_config = AnonymizerConfig.from_json(json)
    assert anonymizer_config.operator_name == class_name
    assert anonymizer_config.params == {"param_1": "my_parameter"}
