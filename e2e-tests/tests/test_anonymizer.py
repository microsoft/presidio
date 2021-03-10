import json

import pytest

from common.assertions import equal_json_strings
from common.methods import anonymize, anonymizers, decrypt


@pytest.mark.api
def test_given_anonymize_called_with_valid_request_then_expected_valid_response_returned():
    request_body = """
    {
        "text": "hello world, my name is Jane Doe. My number is: 034453334",
        "anonymizers": {
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
        "anonymizers": {
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
def test_given_anonymize_called_with_empty_analyzer_results_then_unchanged_text_is_returned():
    request_body = """
    {
        "text": "hello world! nice to meet you!",
        "anonymizers": {
            "DEFAULT": { "type": "replace", "new_value": "ANONYMIZED" },
            "PHONE_NUMBER": { "type": "mask", "masking_char": "*", "chars_to_mask": 4, "from_end": true }
        },
        "analyzer_results": [

        ]
    }
    """
    response_status, response_content = anonymize(request_body)

    expected_response = """{"result":"hello world! nice to meet you!"}"""
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_anonymize_called_with_deformed_body_then_internal_server_error_returned():
    request_body = """
    {
        "text": "hello world, my name is Jane Doe. My number is: 034453334",
        "anonymizers": {
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
        ["hash", "mask", "redact", "replace", "encrypt"]
    """

    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_decrypt_called_with_encrypted_text_then_decrypted_text_returned():

    request_body = """
    {
        "key": "1111111111111111",
        "text": "e6HnOMnIxbd4a8Qea44LshQDnjvxwzBIaAz+YqHNnMW2mC5r3AWoay8Spsoajyyy"
    }
    """

    response_status, response_content = decrypt(request_body)

    expected_response = """
    {
        "result": "text_for_encryption"
    }
    """

    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_decrypt_called_with_invalid_key_then_invalid_input_response_returned():

    request_body = """
    {
        "key": "invalidkey",
        "text": "e6HnOMnIxbd4a8Qea44LshQDnjvxwzBIaAz+YqHNnMW2mC5r3AWoay8Spsoajyyy"
    }
    """

    response_status, response_content = decrypt(request_body)

    expected_response = """
    {
        "error": "Invalid input, key must be of length 128, 192 or 256 bits"
    }
    """

    assert response_status == 422
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_decrypt_called_with_missing_key_then_invalid_input_response_returned():

    request_body = """
    {
        "text": "e6HnOMnIxbd4a8Qea44LshQDnjvxwzBIaAz+YqHNnMW2mC5r3AWoay8Spsoajyyy"
    }
    """

    response_status, response_content = decrypt(request_body)

    expected_response = """
    {
        "error": "Expected parameter key"
    }
    """

    assert response_status == 422
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_decrypt_called_with_missing_text_then_invalid_input_response_returned():

    request_body = """
    {
        "key": "1111111111111111"
    }
    """

    response_status, response_content = decrypt(request_body)

    expected_response = """
    {
        "error": "Expected parameter text"
    }
    """

    assert response_status == 422
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_decrypt_called_with_missing_payload_then_bad_request_response_returned():

    request_body = """
    { }
    """

    response_status, response_content = decrypt(request_body)

    expected_response = """
    {
        "error": "Invalid request json"
    }
    """

    assert response_status == 400
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_encrypt_called_then_decrypt_returns_the_original_encrypted_text():
    text_for_encryption = "text_for_encryption"
    key = "1111111111111111"
    anonymize_request = {
        "text": text_for_encryption,
        "anonymizers": {"DEFAULT": {"type": "encrypt", "key": key}},
        "analyzer_results": [
            {
                "start": 0,
                "end": len(text_for_encryption),
                "score": 0.8,
                "entity_type": "NAME",
            }
        ],
    }
    _, anonymize_response_content = anonymize(json.dumps(anonymize_request))
    encrypted_text = json.loads(anonymize_response_content)["result"]
    decrypt_request = {"text": encrypted_text, "key": key}

    _, decrypt_response_content = decrypt(json.dumps(decrypt_request))

    decrypted_text = json.loads(decrypt_response_content)["result"]
    assert encrypted_text != text_for_encryption
    assert decrypted_text == text_for_encryption
