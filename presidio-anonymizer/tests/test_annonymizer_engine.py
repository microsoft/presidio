import json
import os

import pytest

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.domain import AnonymizerRequest
from presidio_anonymizer.domain import InvalidParamException


def test_engine_result():
    json_path = os.path.dirname(__file__) + "/resources/dup_payload.json"
    with open(json_path) as json_file:
        content = json.load(json_file)
        data = AnonymizerRequest.validate_and_convert(content)
        text = AnonymizerEngine(data).anonymize()
        assert text == 'hello world, my name is <FULL_NAME>. ' \
                       'My number is: <PHONE_NUMBER>'


@pytest.mark.parametrize(
    "request_json, result_text",
    [
        ({}, "Analyze results must contain data.",),
        ({
             "analyzer_results": [
                 {
                     "start": 28,
                     "end": 32,
                     "score": 0.8,
                     "entity_type": "NUMBER"
                 }
             ]
         }, "Please insert a valid text.",),
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
         }, "Invalid anonymizer class 'none'.",)
    ],
)
def test_engine_result_with_empty_text_values_not_failing(request_json, result_text):
    try:
        AnonymizerEngine(request_json).anonymize()
    except InvalidParamException as e:
        assert e.err == result_text
        return
    assert False
