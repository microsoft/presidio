from typing import List

import pytest

from presidio_anonymizer.anonymizers import Replace, Mask
from presidio_anonymizer.entities.anonymizer_request import AnonymizerRequest
from presidio_anonymizer.entities.invalid_exception import InvalidParamException


@pytest.mark.parametrize(
    # fmt: off
    "request_json, result_text",
    [
        ({
             "analyzer_results": [
                 {
                     "end": 32,
                     "score": 0.8,
                 }
             ]
         }, "Invalid input, analyzer result must contain start",),
        ({}, "Invalid input, request must contain analyzer results")
    ],
    # fmt: on
)
def test_given_invalid_json_for_analyzer_result_then_we_fail(
        request_json, result_text
):
    with pytest.raises(InvalidParamException) as e:
        AnonymizerRequest.handle_analyzer_results_json(request_json)
    assert result_text == e.value.err_msg


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
def test_given_invalid_json_for_anonymizers_then_we_fail(
        request_json, result_text
):
    with pytest.raises(InvalidParamException) as e:
        AnonymizerRequest.get_anonymizer_configs_from_json(request_json)
    assert result_text == e.value.err_msg


def test_given_valid_json_then_anonymizers_config_list_created_successfully():
    content = get_content()
    anonymizers_config = AnonymizerRequest.get_anonymizer_configs_from_json(content)
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


def test_given_valid_json_then_analyzer_results_list_created_successfully():
    content = get_content()
    analyzer_results = AnonymizerRequest.handle_analyzer_results_json(content)
    assert len(analyzer_results) == len(content.get("analyzer_results"))
    for result_a in analyzer_results:
        same_result_in_content = __find_element(
            content.get("analyzer_results"), result_a.entity_type
        )
        assert same_result_in_content
        assert result_a.score == same_result_in_content.get("score")
        assert result_a.start == same_result_in_content.get("start")
        assert result_a.end == same_result_in_content.get("end")

def test_given_valid_json_with_no_analyzer_results_then_analyzer_results_list_created_successfully():
    content = get_no_analyzer_results_content()
    analyzer_results = AnonymizerRequest.handle_analyzer_results_json(content)
    assert len(analyzer_results) == len(content.get("analyzer_results"))
    for result_a in analyzer_results:
        same_result_in_content = __find_element(
            content.get("analyzer_results"), result_a.entity_type
        )
        assert same_result_in_content
        assert result_a.score == same_result_in_content.get("score")
        assert result_a.start == same_result_in_content.get("start")
        assert result_a.end == same_result_in_content.get("end")

def __find_element(content: List, entity_type: str):
    for result in content:
        if result.get("entity_type") == entity_type:
            return result
    return None


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

def get_no_analyzer_results_content():
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
        ],
    }