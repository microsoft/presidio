import pytest

from common.assertions import equal_json_strings
from common.methods import anonymize, anonymizers


@pytest.mark.api
def test_given_anonymize_called_with_valid_request_then_expected_valid_response_returned():
    request_body = """
    {
        "text": "hello world, my name is Jane Doe. My number is: 034453334",
        "transformations": {
            "DEFAULT": { "type": "replace", "new_value": "ANONYMIZED" },
            "PHONE_NUMBER": { "type": "mask", "masking_char": "*", "chars_to_mask": 4, "from_end": true }
        },
        "analyzer_results": [
            { "start": 24, "end": 32, "score": 0.8, "entity_type": "NAME" },
            { "start": 24, "end": 28, "score": 0.8, "entity_type": "FIRST_NAME" },
            { "start": 29, "end": 32, "score": 0.6, "entity_type": "LAST_NAME" },
            { "start": 48, "end": 57,  "score": 0.95,
                "entity_type": "PHONE_NUMBER" }
        ]
    }
    """

    response_status, response_content = anonymize(request_body)

    expected_response = (
        """{"result":"hello world, my name is ANONYMIZED. My number is: 03445****"}"""
    )
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_anonymize_called_with_empty_text_then_invalid_input_message_returned():
    request_body = """
    {
        "text": "",
        "transformations": {
            "DEFAULT": { "type": "replace", "new_value": "ANONYMIZED" }
        },
        "analyzer_results": [
            { "start": 24, "end": 32, "score": 0.8, "entity_type": "NAME" }
        ]
    }
    """

    response_status, response_content = anonymize(request_body)

    expected_response = '{"error": "Invalid input, text can not be empty"}'
    assert response_status == 422
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_anonymize_called_with_empty_analyzer_results_then_invalid_input_message_returned():
    request_body = """
    {
        "text": "hello world, my name is Jane Doe. My number is: 034453334",
        "transformations": {
            "DEFAULT": { "type": "replace", "new_value": "ANONYMIZED" },
            "PHONE_NUMBER": { "type": "mask", "masking_char": "*", "chars_to_mask": 4, "from_end": true }
        },
        "analyzer_results": [

        ]
    }
    """
    response_status, response_content = anonymize(request_body)

    expected_response = '{"error": "Invalid input, analyzer results can not be empty"}'
    assert response_status == 422
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_anonymize_called_with_deformed_body_then_internal_server_error_returned():
    request_body = """
    {
        "text": "hello world, my name is Jane Doe. My number is: 034453334",
        "transformations": {
            "DEFAULT": {"type": "replace", "new_value": "ANONYMIZED"},
        },
        "analyzer_results": [
            {"start": 24, "end": 32, "score": 0.8, "entity_type": "NAME"},
            {"start": 24, "end": 28, "score": 0.8, "entity_type": "FIRST_NAME"},
        ]
    }
    """
    response_status, response_content = anonymize(request_body)

    expected_response = '{"error": "Internal server error"}'
    assert response_status == 500
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_anonymizers_called_then_expected_anonymizers_list_returned():

    response_status, response_content = anonymizers()

    expected_response = """
        ["fpe", "hash", "mask", "redact", "replace"]
    """

    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)
