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

    expected_response = """
    {
        "text": "hello world, my name is ANONYMIZED. My number is: 03445****", 
        "items": [
            {"anonymizer": "mask", "entity_type": "PHONE_NUMBER", "start": 50, "end": 59, "anonymized_text": "03445****"}, 
            {"anonymizer": "replace", "entity_type": "NAME", "start": 24, "end": 34, "anonymized_text": "ANONYMIZED"}
        ]
    }
    """
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

    expected_response = """{"text": "hello world! nice to meet you!", "items": []}"""
    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_anonymize_called_with_deformed_body_then_bad_request_error_returned():
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

    expected_response = '{"error": "The browser (or proxy) sent a request that this server could not understand."}'
    assert response_status == 400
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
    text = "e6HnOMnIxbd4a8Qea44LshQDnjvxwzBIaAz+YqHNnMW2mC5r3AWoay8Spsoajyyy"
    request_body = {
        "text": text,
        "encrypt_results": [{
            "start": 0,
            "end": len(text),
            "key": "1111111111111111",
            "entity_type": "NUMBER"
        }],
    }

    response_status, response_content = decrypt(json.dumps(request_body))

    expected_response = """{"text": "text_for_encryption", "items": [{"start": 0, "end": 19, "decrypted_text": "text_for_encryption","entity_type":"NUMBER"}]}"""

    assert response_status == 200
    assert equal_json_strings(expected_response, response_content)


@pytest.mark.api
def test_given_decrypt_called_with_invalid_key_then_invalid_input_response_returned():
    text = "e6HnOMnIxbd4a8Qea44LshQDnjvxwzBIaAz + YqHNnMW2mC5r3AWoay8Spsoajyyy"
    request_body = {
        "text": text,
        "encrypt_results": [{
            "start": 0,
            "end": len(text),
            "entity_type": "number",
            "key": "invalidkey",
        }],
    }

    response_status, response_content = decrypt(json.dumps(request_body))

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

    expected_response = """{"text": "e6HnOMnIxbd4a8Qea44LshQDnjvxwzBIaAz+YqHNnMW2mC5r3AWoay8Spsoajyyy", "items": []}"""
    assert response_status == 200
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
        "error": "Invalid input, text can not be empty"
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
    text_for_encryption = "Lorem Ipsum is a Software Engineer"
    key = "1111111111111111"
    anonymize_request = {
        "text": text_for_encryption,
        "anonymizers": {"DEFAULT": {"type": "encrypt", "key": key},
                        "TITLE": {"type": "encrypt", "key": "2222222222222222"}},
        "analyzer_results": [
            {
                "start": 0,
                "end": 12,
                "score": 0.8,
                "entity_type": "NAME",
            },
            {
                "start": 18,
                "end": len(text_for_encryption),
                "score": 0.8,
                "entity_type": "TITLE",
            }
        ],
    }
    _, anonymize_response_content = anonymize(json.dumps(anonymize_request))
    encrypted_text = json.loads(anonymize_response_content)["text"]

    decrypt_request = {
        "text": encrypted_text,
        "encrypt_results": [
            {
                "start": 0,
                "end": 44,
                "score": 0.8,
                "entity_type": "NAME",
                "key": key,
            },
            {
                "start": 50,
                "end": 114,
                "score": 0.8,
                "entity_type": "TITLE",
                "key": "2222222222222222"
            }
        ],
    }

    _, decrypted_text_response = decrypt(json.dumps(decrypt_request))

    decrypted_text = json.loads(decrypted_text_response)["text"]
    assert decrypted_text == text_for_encryption
