import json
import os

import pytest
from common.methods import anonymize, anonymizers


@pytest.mark.api
def test_anonymize():
    request_body = """
    {
        "text": "hello world, my name is Jane Doe. My number is: 034453334",
        "transformations": {"DEFAULT": {"type": "replace", "new_value": "ANONYMIZED"}},
        "analyzer_results": [
            {"start": 24, "end": 32, "score": 0.8, "entity_type": "NAME"}
        ]
    }
    """
    response_status, response_content = anonymize(request_body)

    expected_response = "hello world, my name is ANONYMIZED. My number is: 034453334"
    assert response_status == 200
    assert expected_response == response_content


@pytest.mark.api
def test_anonymize_with_payload():
    json_path = file_path("payload.json")
    with open(json_path) as json_file:
        content = json.load(json_file)

    response_status, response_content = anonymize(json.dumps(content))

    expected_response = "hello world, my name is ANONYMIZED. My number is: 03445****"
    assert response_status == 200
    assert expected_response == response_content


@pytest.mark.api
def test_anonymize_with_payload_with_intersection_results():
    json_path = file_path("intersection_payload.json")
    with open(json_path) as json_file:
        content = json.load(json_file)

    response_status, response_content = anonymize(json.dumps(content))

    expected_response = "hello world, my name is <FULL_NAME><LAST_NAME> My number is: <PHONE_NUMBER><SSN>"
    assert response_status == 200
    assert expected_response == response_content


@pytest.mark.api
def test_anonymize_api_fails_on_invalid_value_of_text():
    json_path = file_path("payload.json")
    with open(json_path) as json_file:
        content = json.load(json_file)
        content["text"] = ""

    response_status, response_content = anonymize(json.dumps(content))

    expected_response = "Invalid input, text can not be empty"
    assert response_status == 422
    assert response_content == expected_response


@pytest.mark.api
def test_anonymize_with_redact_and_replace():
    json_path = file_path("redact_and_replace_payload.json")
    with open(json_path) as json_file:
        content = json.load(json_file)

    response_status, response_content = anonymize(json.dumps(content))

    expected_response = "hello world, my name is . My number is: <PHONE_NUMBER>"
    assert response_status == 200
    assert response_content == expected_response


def file_path(file_name: str):
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', f"resources/{file_name}"))


@pytest.mark.api
def test_anonymizers():
    expected_list = ["mask", "fpe", "replace", "hash", "redact"]
    response_status, response_content = anonymizers()
    assert response_status == 200
    assert all([a == b for a, b in zip(response_content, expected_list)])
