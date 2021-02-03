import json
import os
from typing import List
from unittest.mock import Mock

import pytest

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.anonymizers import Replace, Mask
from presidio_anonymizer.entities.anonymizer_request import AnonymizerRequest
from presidio_anonymizer.entities.invalid_exception import InvalidParamException


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
def test_given_invalid_json_then_request_creation_should_fail(request_json,
                                                              result_text):
    with pytest.raises(InvalidParamException) as e:
        AnonymizerRequest(request_json, AnonymizerEngine().builtin_anonymizers)
    assert result_text == e.value.err_msg


def test_given_no_transformations_then_we_get_the_default():
    content = get_content()
    request = AnonymizerRequest(content, AnonymizerEngine().builtin_anonymizers)
    request._transformations = {}
    analyzer_result = Mock()
    analyzer_result.entity_type = "PHONE"
    transformation = request.get_transformation(analyzer_result)
    assert transformation.get("type") == "replace"
    assert type(transformation.get("anonymizer")) == type(Replace)


def test_given_valid_json_then_request_creation_should_succeed():
    content = get_content()
    data = AnonymizerRequest(content, AnonymizerEngine().builtin_anonymizers)
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


def test_given_valid_anonymizer_request_then_get_transformations_successfully():
    content = get_content()
    data = AnonymizerRequest(content, AnonymizerEngine().builtin_anonymizers)
    replace_result = data.get_analysis_results()[0]
    default_replace_transformation = data.get_transformation(replace_result)
    assert default_replace_transformation.get('type') == 'replace'
    assert default_replace_transformation.get('new_value') == 'ANONYMIZED'
    assert type(default_replace_transformation.get('anonymizer')) == type(Replace)
    mask_transformation = data.get_transformation(data.get_analysis_results()[3])
    assert mask_transformation.get('type') == 'mask'
    assert mask_transformation.get('from_end')
    assert mask_transformation.get('chars_to_mask') == 4
    assert mask_transformation.get('masking_char') == '*'
    assert mask_transformation.get('anonymizer')
    assert type(mask_transformation.get('anonymizer')) == type(Mask)


def __find_element(content: List, entity_type: str):
    for result in content:
        if result.get("entity_type") == entity_type:
            return result
    return None


def file_path(file_name: str):
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), f"resources/{file_name}"))


content = {}


def get_content():
    global content
    json_path = file_path("payload.json")
    with open(json_path) as json_file:
        content = json.load(json_file)
        return content
