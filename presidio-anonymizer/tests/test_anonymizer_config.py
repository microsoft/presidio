import pytest

from presidio_anonymizer.entities import AnonymizerConfig


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
    assert anonymizer_config.anonymizer_name == class_name
    assert anonymizer_config.params == {"param_1": "my_parameter"}


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
