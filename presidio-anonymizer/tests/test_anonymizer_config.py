import pytest

from presidio_anonymizer.entities import AnonymizerConfig, InvalidParamException
from presidio_anonymizer.operators import Mask, Replace


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
    assert anonymizer_config.anonymizer_class
    assert anonymizer_config.anonymizer_class().operator_name() == class_name
    assert anonymizer_config.params == {"param_1": "my_parameter"}


@pytest.mark.parametrize(
    # fmt: off
    "class_name",
    [
        "", "Hash", "NONE"
    ],
    # fmt: on
)
def test_given_json_with_bad_anonymizer_name_then_we_fail(class_name):
    json = {"type": class_name, "param_1": "my_parameter"}
    with pytest.raises(
            InvalidParamException, match=f"Invalid anonymizer class '{class_name}'."
    ):
        AnonymizerConfig.from_json(json)


@pytest.mark.parametrize(
    # fmt: off
    "request_json, result_text",
    [
        ({
             "anonymizers": {
                 "default": {
                     "type": "none"
                 }
             }
         }, "Invalid anonymizer class 'none'.",),
        ({
             "anonymizers": {
                 "number": {

                 }
             }
         }, "Invalid anonymizer class 'None'.",),
    ],
    # fmt: on
)
def test_given_invalid_json_for_anonymizers_then_we_fail(request_json, result_text):
    with pytest.raises(InvalidParamException) as e:
        AnonymizerConfig.get_anonymizer_configs_from_json(request_json)
    assert result_text == e.value.err_msg


def test_given_valid_json_then_anonymizers_config_list_created_successfully():
    content = get_content()
    anonymizers_config = AnonymizerConfig.get_anonymizer_configs_from_json(content)
    assert len(anonymizers_config) == 2
    phone_number_anonymizer = anonymizers_config.get("PHONE_NUMBER")
    assert phone_number_anonymizer.params == {
        "masking_char": "*",
        "chars_to_mask": 4,
        "from_end": True,
    }
    assert phone_number_anonymizer.anonymizer_class == Mask
    default_anonymizer = anonymizers_config.get("DEFAULT")
    assert default_anonymizer.params == {"new_value": "ANONYMIZED"}
    assert default_anonymizer.anonymizer_class == Replace


def get_content():
    return {
        "text": "hello world, my name is Jane Doe. My number is: 034453334",
        "anonymizers": {
            "DEFAULT": {"type": "replace", "new_value": "ANONYMIZED"},
            "PHONE_NUMBER": {
                "type": "mask",
                "masking_char": "*",
                "chars_to_mask": 4,
                "from_end": True,
            },
        },
        "analyzer_results": [
            {"start": 24, "end": 32, "score": 0.8, "entity_type": "NAME"},
            {"start": 24, "end": 28, "score": 0.8, "entity_type": "FIRST_NAME"},
            {"start": 29, "end": 32, "score": 0.6, "entity_type": "LAST_NAME"},
            {"start": 48, "end": 57, "score": 0.95, "entity_type": "PHONE_NUMBER"},
        ],
    }
