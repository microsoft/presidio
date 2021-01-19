import json
import os
from typing import List

import pytest

from presidio_anonymizer.domain.analyzer_result import AnalyzerResult
from presidio_anonymizer.domain.analyzer_results import AnalyzerResults
from presidio_anonymizer.domain.invalid_exception import InvalidJsonException
from presidio_anonymizer.domain.anonymizer_request import AnonymizerRequest


@pytest.mark.parametrize(
    "request_json, result_text",
    [
        ({}, "Invalid json, analyzer result must contain start",),
        ({
             "end": 32,
             "score": 0.8,
             "entity_type": "NUMBER"
         }, "Invalid json, analyzer result must contain start",),
        ({
             "start": 28,
             "score": 0.8,
             "entity_type": "NUMBER"
         }, "Invalid json, analyzer result must contain end",),
        ({
             "start": 28,
             "end": 32,
             "entity_type": "NUMBER"
         }, "Invalid json, analyzer result must contain score",),
        ({
             "start": 28,
             "end": 32,
             "score": 0.8,
         }, "Invalid json, analyzer result must contain entity_type",),
    ],
)
def test_analyzer_result_invalid_json_formats(request_json, result_text):
    try:
        AnalyzerResult.validate_and_create(request_json)
    except InvalidJsonException as e:
        assert e.err == result_text
    except Exception as e:
        assert not e


def test_analyzer_result_valid_json():
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
    "request_json, result_text",
    [
        ({}, "Invalid json, analyzer results can not be empty",),
        ({
             "text": "hello world, my name is Jane Doe. My number is: 034453334",
             "analyzer_results": [
                 {
                     "end": 32,
                     "score": 0.8,
                 }
             ]
         }, "Invalid json, analyzer result must contain start",),
        ({
             "text": "hello world, my name is Jane Doe. My number is: 034453334",
         }, "Invalid json, analyzer results can not be empty",),
        ({
             "analyzer_results": [
                 {
                     "start": 28,
                     "end": 32,
                     "score": 0.8,
                     "entity_type": "NUMBER"
                 }
             ]
         }, "Invalid json, text can not be empty",)
    ],
)
def test_request_invalid_json_formats(request_json, result_text):
    try:
        AnonymizerRequest.validate_and_convert(request_json)
    except InvalidJsonException as e:
        assert e.err == result_text
    except Exception as e:
        assert not e


def test_request_valid_json():
    json_path = os.path.dirname(__file__) + "/resources/payload.json"
    with open(json_path) as json_file:
        content = json.load(json_file)
        data = AnonymizerRequest.validate_and_convert(content)
        assert data.get("text") == content.get("text")
        assert data.get("transformations") == content.get("transformations")
        assert len(data.get("analyzer_results")) == len(content.get("analyzer_results"))
        for result_a in data.get("analyzer_results"):
            result_b = __find_element(content.get("analyzer_results"),
                                      result_a.entity_type)
            assert result_b
            assert result_a.score == result_b.get("score")
            assert result_a.start == result_b.get("start")
            assert result_a.end == result_b.get("end")


def test_analyzer_results_sorted_set():
    json_path = os.path.dirname(__file__) + "/resources/dup_payload.json"
    with open(json_path) as json_file:
        content = json.load(json_file)
        data = AnonymizerRequest.validate_and_convert(content)
        analyze_results = data.get("analyzer_results")
        assert len(analyze_results) == len(content.get("analyzer_results"))
        sorted_results = analyze_results.to_sorted_set()
        assert len(sorted_results) == 2
        assert list(sorted_results)[0].start < list(sorted_results)[1].start
        assert list(sorted_results)[0].end < list(sorted_results)[1].end
        assert list(sorted_results)[0].score < list(sorted_results)[1].score


def test_analyzer_results_not_failing_on_empty_list():
    analyzer_result = AnalyzerResults()
    assert len(analyzer_result.to_sorted_set()) == 0


def __find_element(content: List, entity_type: str):
    for result in content:
        if result.get("entity_type") == entity_type:
            return result
    return None
