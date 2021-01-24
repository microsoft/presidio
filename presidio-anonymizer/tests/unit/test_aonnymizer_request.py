import json
import os
from typing import List

import pytest

from presidio_anonymizer.anonymizers import Anonymizer, Replace, Mask
from presidio_anonymizer.entities.anonymizer_request import AnonymizerRequest
from presidio_anonymizer.entities.invalid_exception import InvalidParamException


@pytest.mark.parametrize(
    # fmt: off
    "request_json, result_text",
    [
        ({}, "Invalid input, analyzer result must contain start",),
        ({
             "end": 32,
             "score": 0.8,
             "entity_type": "NUMBER"
         }, "Invalid input, analyzer result must contain start",),
        ({
             "start": 28,
             "score": 0.8,
             "entity_type": "NUMBER"
         }, "Invalid input, analyzer result must contain end",),
        ({
             "start": 28,
             "end": 32,
             "entity_type": "NUMBER"
         }, "Invalid input, analyzer result must contain score",),
        ({
             "start": 28,
             "end": 32,
             "score": 0.8,
         }, "Invalid input, analyzer result must contain entity_type",),
    ],
    # fmt: on
)
def test_analyzer_result_fails_on_invalid_json_formats(request_json, result_text):
    try:
        AnalyzerResult.validate_and_create(request_json)
    except InvalidParamException as e:
        assert e.err_msg == result_text
    except Exception as e:
        assert not e


def test_analyzer_result_pass_with_valid_json():
    content = {
        "start": 0,
        "end": 32,
        "score": 0.8,
        "entity_type": "NUMBER"
    }
    data = AnalyzerResult.validate_and_create(content)
    assert data.start == content.get("start")
    assert data.end == content.get("end")
    assert data.score == content.get("score")
    assert data.entity_type == content.get("entity_type")


@pytest.mark.parametrize(
    # fmt: off
    "request_json, result_text",
    [
        ({}, "Invalid input, analyzer results can not be empty",),
        ({
             "text": "Hello world",
             "analyzer_results": [
                 {
                     "start": 28,
                     "end": 32,
                     "score": 0.8,
                     "entity_type": "NUMBER"
                 }
             ],
             "transformations": {
                 "default": {
                     "type": "none"
                 }
             }
         }, "Invalid anonymizer class 'none'.",),
        ({
             "text": "hello world, my name is Jane Doe. My number is: 034453334",
             "analyzer_results": [
                 {
                     "end": 32,
                     "score": 0.8,
                 }
             ]
         }, "Invalid input, analyzer result must contain start",),
        ({
             "text": "hello world, my name is Jane Doe. My number is: 034453334",
         }, "Invalid input, analyzer results can not be empty",),
        ({
             "analyzer_results": [
                 {
                     "start": 28,
                     "end": 32,
                     "score": 0.8,
                     "entity_type": "NUMBER"
                 }
             ]
         }, "Invalid input, text can not be empty",)
    ],
    # fmt: on
)
def test_creating_anonymizer_request_should_fail_over_validation(request_json,
                                                                 result_text):
    try:
        AnonymizerRequest(request_json)
    except InvalidParamException as e:
        assert e.err_msg == result_text
    except Exception as e:
        assert not e


def test_anonymizer_request_pass_on_valid_json():
    json_path = file_path("payload.json")
    with open(json_path) as json_file:
        content = json.load(json_file)
        data = AnonymizerRequest(content)
        assert data.get_text() == content.get("text")
        assert data._text == content.get("text")
        assert data._transformations == content.get("transformations")
        assert len(data._analysis_results) == len(content.get("analyzer_results"))
        assert data._analysis_results == data.get_analysis_results()
        for result_a in data._analysis_results:
            same_result_in_content = __find_element(content.get("analyzer_results"),
                                                    result_a.entity_type)
            assert same_result_in_content
            assert result_a.score == same_result_in_content.get("score")
            assert result_a.start == same_result_in_content.get("start")
            assert result_a.end == same_result_in_content.get("end")
            assert data.get_transformation(result_a)


def test_anonymizer_get_transformation_successfully():
    json_path = file_path("payload.json")
    with open(json_path) as json_file:
        content = json.load(json_file)
        data = AnonymizerRequest(content)
        replace_result = data.get_analysis_results()[0]
        default_replace_transformation = data.get_transformation(replace_result)
        assert default_replace_transformation.get('type') == 'replace'
        assert default_replace_transformation.get('new_value') == 'ANONYMIZED'
        assert issubclass(default_replace_transformation.get('anonymizer'), Anonymizer)
        assert issubclass(default_replace_transformation.get('anonymizer'), Replace)
        mask_transformation = data.get_transformation(data.get_analysis_results()[3])
        assert mask_transformation.get('type') == 'mask'
        assert mask_transformation.get('from_end')
        assert mask_transformation.get('chars_to_mask') == 4
        assert mask_transformation.get('masking_char') == '*'
        assert mask_transformation.get('anonymizer')
        assert issubclass(mask_transformation.get('anonymizer'), Anonymizer)
        assert issubclass(mask_transformation.get('anonymizer'), Mask)


def __find_element(content: List, entity_type: str):
    for result in content:
        if result.get("entity_type") == entity_type:
            return result
    return None


def file_path(file_name: str):
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', f"resources/{file_name}"))
