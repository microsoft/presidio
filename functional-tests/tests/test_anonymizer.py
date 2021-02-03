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
            { "start": 48, "end": 57,  "score": 0.95, "entity_type": "PHONE_NUMBER" }
        ]
    }
    """

    response_status, response_content = anonymize(request_body)

    expected_response = "hello world, my name is ANONYMIZED. My number is: 03445****"
    assert response_status == 200
    assert response_content == expected_response


@pytest.mark.api
def test_anonymize_hash_called_with_valid_request_then_expected_valid_response_returned():
    request_body = """
    {
        "text": "hello world, my name is Jane Doe. My number is: 034453334",
        "transformations": {
            "DEFAULT": { "type": "hash", "hash_type": "sha512" },
        },
        "analyzer_results": [
            { "start": 24, "end": 32, "score": 0.8, "entity_type": "NAME" },
            { "start": 24, "end": 28, "score": 0.8, "entity_type": "FIRST_NAME" },
            { "start": 29, "end": 32, "score": 0.6, "entity_type": "LAST_NAME" },
            { "start": 48, "end": 57,  "score": 0.95, "entity_type": "PHONE_NUMBER" }
        ]
    }
    """

    response_status, response_content = anonymize(request_body)

    expected_response = "hello world, my name is 508789e7c17beebf2f17e611b43920792b692"
    "ad9ae53f9be3a947b04fbf820f40d57f42864a20e7121180e9467fda3fa2480e50c0da15244b6153ab"
    "e2509362c. My number is: 8ea244bbf71264237db23324b3ff83f6ef6601c9da08af42122f992ec4"
    "5d757c3efd953185b2590e4542aa1ca3637fa8935ebff2b43af0ea1245e7c843fbebdc"
    assert response_status == 200
    assert response_content == expected_response


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

    expected_response = "Invalid input, text can not be empty"
    assert response_status == 422
    assert response_content == expected_response


@pytest.mark.api
def test_given_anonymizers_called_then_expected_builtin_anonymizers_list_returned():

    response_status, response_content = anonymizers()

    expected_response = """
        ["mask", "fpe", "replace", "hash", "redact"]
    """

    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)
