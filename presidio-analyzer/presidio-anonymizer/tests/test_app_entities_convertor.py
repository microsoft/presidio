from typing import List

import pytest

from presidio_anonymizer.entities import (
    InvalidParamError,
    RecognizerResult,
    OperatorConfig,
)
from presidio_anonymizer.services.app_entities_convertor import AppEntitiesConvertor


def test_given_valid_json_then_anonymizers_config_list_created_successfully():
    content = get_content()
    anonymizers_config = AppEntitiesConvertor.operators_config_from_json(
        content.get("anonymizers")
    )
    assert len(anonymizers_config) == 2
    phone_number_anonymizer = anonymizers_config.get("PHONE_NUMBER")
    assert phone_number_anonymizer.params == {
        "masking_char": "*",
        "chars_to_mask": 4,
        "from_end": True,
    }
    assert phone_number_anonymizer.operator_name == "mask"
    default_anonymizer = anonymizers_config.get("DEFAULT")
    assert default_anonymizer.params == {"new_value": "ANONYMIZED"}
    assert default_anonymizer.operator_name == "replace"


@pytest.mark.parametrize(
    # fmt: off
    "request_json, result_text",
    [
        (
                [
                    {
                        "end": 32,
                        "score": 0.8,
                    }
                ]
                , "Invalid input, result must contain start",),
        (None, "Invalid input, request must contain analyzer results")
    ],
    # fmt: on
)
def test_given_invalid_json_for_analyzer_result_then_we_fail(request_json, result_text):
    with pytest.raises(InvalidParamError) as e:
        AppEntitiesConvertor.analyzer_results_from_json(request_json)
    assert result_text == e.value.err_msg


def test_given_valid_json_then_analyzer_results_list_created_successfully():
    content = get_content().get("analyzer_results")
    analyzer_results = AppEntitiesConvertor.analyzer_results_from_json(content)
    assert len(analyzer_results) == len(content)
    for result_a in analyzer_results:
        same_result_in_content = __find_element(content, result_a.entity_type)
        assert same_result_in_content
        assert result_a.score == same_result_in_content.get("score")
        assert result_a.start == same_result_in_content.get("start")
        assert result_a.end == same_result_in_content.get("end")


def test_given_empty_analyzer_results_then_list_created_successfully():
    analyzer_results = AppEntitiesConvertor.analyzer_results_from_json([])
    assert len(analyzer_results) == len([])
    for result_a in analyzer_results:
        same_result_in_content = __find_element([], result_a.entity_type)
        assert same_result_in_content
        assert result_a.score == same_result_in_content.get("score")
        assert result_a.start == same_result_in_content.get("start")
        assert result_a.end == same_result_in_content.get("end")


@pytest.mark.parametrize(
    "anonymizer_json, result",
    [
        ({"anonymizers": {}}, {}),
        ({}, {}),
        (
            {"anonymizers": {"PHONE": {"type": "replace"}}},
            {"PHONE": OperatorConfig("replace")},
        ),
        (
            {
                "anonymizers": {
                    "PHONE": {"type": "redact", "param": "param", "param_1": "param_1"}
                }
            },
            {
                "PHONE": OperatorConfig(
                    "redact", {"param": "param", "param_1": "param_1"}
                )
            },
        ),
    ],
)
def test_given_anonymizers_json_then_we_create_properties_properly(
    anonymizer_json, result
):
    anonymizers_config = AppEntitiesConvertor.operators_config_from_json(
        anonymizer_json.get("anonymizers")
    )
    assert anonymizers_config == result


@pytest.mark.parametrize(
    "analyzer_json, result",
    [
        ([], []),
        (
            [{"start": 24, "end": 32, "score": 0.8, "entity_type": "NAME"}],
            [RecognizerResult("NAME", 24, 32, 0.8)],
        ),
    ],
)
def test_given_anonymize_called_with_multiple_scenarios_then_expected_results_returned(
    analyzer_json, result
):
    analyzer_results = AppEntitiesConvertor.analyzer_results_from_json(analyzer_json)

    assert analyzer_results == result


def test_given_valid_json_then_we_convert_it_to_decrypt_entities_list():
    data = {
        "text": "THIS IS MY TEXT",
        "anonymizer_results": [{"start": 0, "end": 5, "entity_type": "PHONE"}],
    }
    decrypted_entities = AppEntitiesConvertor.deanonymize_entities_from_json(data)
    assert len(decrypted_entities) == 1
    assert decrypted_entities[0].start == 0
    assert decrypted_entities[0].end == 5
    assert decrypted_entities[0].entity_type == "PHONE"


def test_given_invalid_json_then_we_fail_to_convert():
    data = {
        "text": "THIS IS MY TEXT",
        "anonymizer_results": [
            {
                "start": 0,
                "end": 5,
                "key": "1111111111111111",
            }
        ],
    }
    with pytest.raises(
        InvalidParamError, match="Invalid input, result must contain entity_type"
    ):
        AppEntitiesConvertor.deanonymize_entities_from_json(data)


def test_given_nullified_anonymizer_results_json_we_convert_it_to_empty_entities_list():
    data = {
        "text": "THIS IS MY TEXT",
    }
    decrypted_entities = AppEntitiesConvertor.deanonymize_entities_from_json(data)
    assert len(decrypted_entities) == 0


def test_given_custom_operator_then_expected_result_returned():
    result = True
    anonymizers = {
        "DEFAULT": {"type": "replace", "new_value": "ANONYMIZED"},
        "PHONE_NUMBER": {"type": "custom", "lambda": "lambda x: x[::-1]"},
    }
    anonymizers_config = AppEntitiesConvertor.operators_config_from_json(anonymizers)
    assert AppEntitiesConvertor.check_custom_operator(anonymizers_config) == result


def test_given_no_custom_operator_then_expected_result_returned():
    result = False
    content = get_content()
    anonymizers_config = AppEntitiesConvertor.operators_config_from_json(
        content.get("anonymizers")
    )
    assert AppEntitiesConvertor.check_custom_operator(anonymizers_config) == result


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


def __find_element(content: List, entity_type: str):
    for result in content:
        if result.get("entity_type") == entity_type:
            return result
    return None
