import json

import pytest

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import (
    AnonymizerRequest,
    RecognizerResult,
    AnonymizerConfig,
    AnonymizerResult)
from presidio_anonymizer.entities.anonymizer_result_item import AnonymizerResultItem
from presidio_anonymizer.services.aes_cipher import AESCipher
from tests.integration.file_utils import get_scenario_file_content


@pytest.mark.parametrize(
    "anonymize_scenario",
    [
        "mask_name_phone_number",
        "redact_and_replace",
        "replace_with_intersecting_entities",
        "hash_md5",
        "hash_sha256",
        "hash_sha512",
        "hash_sha256_default",
    ],
)
def test_given_anonymize_called_with_multiple_scenarios_then_expected_results_returned(
    anonymize_scenario,
):
    anonymizer_request_dict = json.loads(
        get_scenario_file_content("anonymize", f"{anonymize_scenario}.in.json")
    )
    expected_anonymize_result_json = json.loads(
        get_scenario_file_content("anonymize", f"{anonymize_scenario}.out.json")
    )
    items = []
    for item in expected_anonymize_result_json['items']:
        items.append(AnonymizerResultItem(item['anonymizer'],
                                          item['entity_type'],
                                          item['start'],
                                          item['end'],
                                          item['anonymized_text'],))
    expected_anonymize_result = AnonymizerResult(expected_anonymize_result_json['text'], items)
    engine = AnonymizerEngine()
    anonymizers_config = AnonymizerRequest.get_anonymizer_configs_from_json(
        anonymizer_request_dict
    )
    analyzer_results = AnonymizerRequest.handle_analyzer_results_json(
        anonymizer_request_dict
    )

    try:
        actual_anonymize_result = engine.anonymize(
            anonymizer_request_dict.get("text"), analyzer_results, anonymizers_config
        )
    except Exception as e:
        actual_anonymize_result = str(e)

    assert actual_anonymize_result == expected_anonymize_result


@pytest.mark.parametrize(
    "anonymize_scenario",
    [
        "mask_phone_number_with_bad_masking_char",
    ],
)
def test_given_anonymize_called_with_error_scenarios_then_expected_errors_returned(
    anonymize_scenario,
):
    anonymizer_request_dict = json.loads(
        get_scenario_file_content("anonymize", f"{anonymize_scenario}.in.json")
    )
    expected_anonymize_result_json = json.loads(
        get_scenario_file_content("anonymize", f"{anonymize_scenario}.out.json")
    )
    engine = AnonymizerEngine()
    anonymizers_config = AnonymizerRequest.get_anonymizer_configs_from_json(
        anonymizer_request_dict
    )
    analyzer_results = AnonymizerRequest.handle_analyzer_results_json(
        anonymizer_request_dict
    )

    try:
        actual_anonymize_result = engine.anonymize(
            anonymizer_request_dict.get("text"), analyzer_results, anonymizers_config
        )
    except Exception as e:
        actual_anonymize_result = str(e)

    assert actual_anonymize_result == expected_anonymize_result_json


def test_given_anonymize_with_encrypt_then_text_returned_with_encrypted_content():
    unencrypted_text = "My name is "
    expected_encrypted_text = "Chloë"
    text = unencrypted_text + expected_encrypted_text
    start_index = 11
    end_index = 16
    key = "WmZq4t7w!z%C&F)J"
    analyzer_results = [RecognizerResult("PERSON", start_index, end_index, 0.8)]
    anonymizers_config = {"PERSON": AnonymizerConfig("encrypt", {"key": key})}

    actual_anonymize_result = AnonymizerEngine().anonymize(
        text, analyzer_results, anonymizers_config
    ).text

    assert actual_anonymize_result[:start_index] == unencrypted_text
    actual_encrypted_text = actual_anonymize_result[start_index:]
    assert actual_encrypted_text != expected_encrypted_text
    actual_decrypted_text = AESCipher.decrypt(key.encode(), actual_encrypted_text)
    assert actual_decrypted_text == expected_encrypted_text
