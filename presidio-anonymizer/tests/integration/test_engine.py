import pytest

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import (
    RecognizerResult,
    AnonymizerConfig,
)
from presidio_anonymizer.services.aes_cipher import AESCipher


def test_given_name_and_phone_number_then_we_anonymize_successfully():
    text = "hello world, my name is Jane Doe. My number is: 03-4453334"
    anonymizer_config = {"DEFAULT": AnonymizerConfig("mask", {"masking_char": "*",
                                                              "chars_to_mask": 20,
                                                              "from_end": False}),
                         "PHONE_NUMBER": AnonymizerConfig("mask", {"masking_char": "*",
                                                                   "chars_to_mask": 6,
                                                                   "from_end": True})
                         }
    analyzer_results = [
        RecognizerResult(
            start=24,
            end=32,
            score=0.8,
            entity_type="NAME"
        ),
        RecognizerResult(
            start=48,
            end=57,
            score=0.95,
            entity_type="PHONE_NUMBER"
        )
    ]
    expected_result = """{"text": "hello world, my name is ********. My number is: 03-******4", "items": [{"start": 48, "end": 57, "anonymized_text": "03-******", "entity_type": "PHONE_NUMBER", "anonymizer": "mask"}, {"start": 24, "end": 32, "anonymized_text": "********", "entity_type": "NAME", "anonymizer": "mask"}]}"""
    run_engine_and_validate(text, anonymizer_config, analyzer_results, expected_result)


def test_given_redact_and_replace_then_we_anonymize_successfully():
    text = "hello world, my name is Jane Doe. My number is: 03-4453334"
    anonymizer_config = {
        "NAME": AnonymizerConfig("redact", {"new_value": "ANONYMIZED"}),
        "PHONE_NUMBER": AnonymizerConfig("replace", {"new_value": ""})}
    analyzer_results = [
        RecognizerResult(
            start=24,
            end=32,
            score=0.8,
            entity_type="NAME"
        ),
        RecognizerResult(
            start=48,
            end=57,
            score=0.95,
            entity_type="PHONE_NUMBER"
        )
    ]
    expected_result = """{"text": "hello world, my name is . My number is: <PHONE_NUMBER>4", "items": [{"start": 40, "end": 54, "anonymized_text": "<PHONE_NUMBER>", "entity_type": "PHONE_NUMBER", "anonymizer": "replace"}, {"start": 24, "end": 24, "anonymized_text": "", "entity_type": "NAME", "anonymizer": "redact"}]}"""
    run_engine_and_validate(text, anonymizer_config, analyzer_results, expected_result)


def test_given_intersacting_entities_then_we_anonymize_correctly():
    text = "hello world, my name is Jane Doe. My number is: 03-4453334"
    anonymizer_config = {
        "NAME": AnonymizerConfig("redact", {"new_value": "ANONYMIZED"}),
        "PHONE_NUMBER": AnonymizerConfig("replace", {"new_value": ""})}
    analyzer_results = [
        RecognizerResult(
            start=24,
            end=32,
            score=0.8,
            entity_type="NAME"
        ),
        RecognizerResult(
            start=48,
            end=57,
            score=0.95,
            entity_type="PHONE_NUMBER"
        )
    ]
    run_engine_and_validate(text, anonymizer_config, analyzer_results, "")


def test_given_intersacting_entities_then_we_anonymize_correctly():
    text = "hello world, my name is Jane Doe. My number is: 03-4453334"
    anonymizer_config = {}
    analyzer_results = [
        RecognizerResult(
            start=24,
            end=32,
            score=0.6,
            entity_type="FULL_NAME"
        ),
        RecognizerResult(
            start=48,
            end=56,
            score=0.95,
            entity_type="PHONE_NUMBER"
        ),
        RecognizerResult(
            start=54,
            end=57,
            score=0.8,
            entity_type="SSN"
        ),
        RecognizerResult(
            start=24,
            end=28,
            score=0.9,
            entity_type="FIRST_NAME"
        ),
        RecognizerResult(
            start=29,
            end=33,
            score=0.6,
            entity_type="LAST_NAME"
        ),
        RecognizerResult(
            start=24,
            end=30,
            score=0.8,
            entity_type="NAME"
        )
    ]
    expected_result = """{"text": "hello world, my name is <FULL_NAME><LAST_NAME> My number is: <PHONE_NUMBER><SSN>4", "items": [{"start": 75, "end": 80, "anonymized_text": "<SSN>", "entity_type": "SSN", "anonymizer": "replace"}, {"start": 61, "end": 75, "anonymized_text": "<PHONE_NUMBER>", "entity_type": "PHONE_NUMBER", "anonymizer": "replace"}, {"start": 35, "end": 46, "anonymized_text": "<LAST_NAME>", "entity_type": "LAST_NAME", "anonymizer": "replace"}, {"start": 24, "end": 35, "anonymized_text": "<FULL_NAME>", "entity_type": "FULL_NAME", "anonymizer": "replace"}]}"""
    run_engine_and_validate(text, anonymizer_config, analyzer_results, expected_result)


@pytest.mark.parametrize(
    # fmt: off
    "hash_type,result",
    [
        ("md5",
         """{"text": "hello world, my name is 1c272047233576d77a9b9a1acfdf741c. My number is: e7706047f07bf68a5dd73e8c47db3a30", "items": [{"start": 72, "end": 104, "anonymized_text": "e7706047f07bf68a5dd73e8c47db3a30", "entity_type": "PHONE_NUMBER", "anonymizer": "hash"}, {"start": 24, "end": 56, "anonymized_text": "1c272047233576d77a9b9a1acfdf741c", "entity_type": "NAME", "anonymizer": "hash"}]}"""),
        ("sha256",
         """{"text": "hello world, my name is 01332c876518a793b7c1b8dfaf6d4b404ff5db09b21c6627ca59710cc24f696a. My number is: 230451ebc7df208f1d5227aceaebf6d8e936f17d74330a5a5c5cbbd4e41d0d57", "items": [{"start": 104, "end": 168, "anonymized_text": "230451ebc7df208f1d5227aceaebf6d8e936f17d74330a5a5c5cbbd4e41d0d57", "entity_type": "PHONE_NUMBER", "anonymizer": "hash"}, {"start": 24, "end": 88, "anonymized_text": "01332c876518a793b7c1b8dfaf6d4b404ff5db09b21c6627ca59710cc24f696a", "entity_type": "NAME", "anonymizer": "hash"}]}"""),
        ("sha512",
         """{"text": "hello world, my name is 508789e7c17beebf2f17e611b43920792b692ad9ae53f9be3a947b04fbf820f40d57f42864a20e7121180e9467fda3fa2480e50c0da15244b6153abe2509362c. My number is: 8ea244bbf71264237db23324b3ff83f6ef6601c9da08af42122f992ec45d757c3efd953185b2590e4542aa1ca3637fa8935ebff2b43af0ea1245e7c843fbebdc", "items": [{"start": 168, "end": 296, "anonymized_text": "8ea244bbf71264237db23324b3ff83f6ef6601c9da08af42122f992ec45d757c3efd953185b2590e4542aa1ca3637fa8935ebff2b43af0ea1245e7c843fbebdc", "entity_type": "PHONE_NUMBER", "anonymizer": "hash"}, {"start": 24, "end": 152, "anonymized_text": "508789e7c17beebf2f17e611b43920792b692ad9ae53f9be3a947b04fbf820f40d57f42864a20e7121180e9467fda3fa2480e50c0da15244b6153abe2509362c", "entity_type": "NAME", "anonymizer": "hash"}]}"""),
        ("",
         """{"text": "hello world, my name is 01332c876518a793b7c1b8dfaf6d4b404ff5db09b21c6627ca59710cc24f696a. My number is: 230451ebc7df208f1d5227aceaebf6d8e936f17d74330a5a5c5cbbd4e41d0d57", "items": [{"start": 104, "end": 168, "anonymized_text": "230451ebc7df208f1d5227aceaebf6d8e936f17d74330a5a5c5cbbd4e41d0d57", "entity_type": "PHONE_NUMBER", "anonymizer": "hash"}, {"start": 24, "end": 88, "anonymized_text": "01332c876518a793b7c1b8dfaf6d4b404ff5db09b21c6627ca59710cc24f696a", "entity_type": "NAME", "anonymizer": "hash"}]}""")
    ],
    # fmt: on
)
def test_given_hash_then_we_anonymize_correctly(hash_type, result):
    text = "hello world, my name is Jane Doe. My number is: 034453334"
    params = {}
    if hash_type:
        params = {"hash_type": hash_type}
    anonymizer_config = {
        "DEFAULT": AnonymizerConfig("hash", params)}
    analyzer_results = [
        RecognizerResult(
            start=48,
            end=57,
            score=0.95,
            entity_type="PHONE_NUMBER"
        ),
        RecognizerResult(
            start=24,
            end=28,
            score=0.8,
            entity_type="FIRST_NAME"
        ),
        RecognizerResult(
            start=29,
            end=32,
            score=0.6,
            entity_type="LAST_NAME"
        ),
        RecognizerResult(
            start=24,
            end=32,
            score=0.8,
            entity_type="NAME"
        )
    ]
    run_engine_and_validate(text, anonymizer_config, analyzer_results, result)


def run_engine_and_validate(text: str, anonymizers_config, analyzer_results,
                            expected_result):
    engine = AnonymizerEngine()
    try:
        actual_anonymize_result = engine.anonymize(
            text, analyzer_results, anonymizers_config
        )
    except Exception as e:
        actual_anonymize_result = str(e)

    assert actual_anonymize_result.to_json() == expected_result


def test_given_anonymize_called_with_error_scenarios_then_expected_errors_returned():
    text = "hello world, my name is Jane Doe. My number is: 03-4453334"
    anonymizers = {
        "PHONE_NUMBER": AnonymizerConfig("mask", {"masking_char": "non_character",
                                                  "chars_to_mask": 6,
                                                  "from_end": True})}
    analyzer_results = [RecognizerResult("PHONE_NUMBER", 48, 57, 0.95)]

    engine = AnonymizerEngine()

    try:
        actual_anonymize_result = engine.anonymize(
            text, analyzer_results, anonymizers
        )
    except Exception as e:
        actual_anonymize_result = str(e)

    assert actual_anonymize_result == "Invalid input, masking_char must be a character"


def test_given_anonymize_with_encrypt_then_text_returned_with_encrypted_content():
    unencrypted_text = "My name is "
    expected_encrypted_text = "Chloë"
    text = unencrypted_text + expected_encrypted_text
    start_index = 11
    end_index = 16
    key = "WmZq4t7w!z%C&F)J"
    analyzer_results = [RecognizerResult("PERSON", start_index, end_index, 0.8)]
    anonymizers_config = {"PERSON": AnonymizerConfig("encrypt", {"key": key})}

    actual_anonymize_result = (
        AnonymizerEngine().anonymize(text, analyzer_results, anonymizers_config).text
    )

    assert actual_anonymize_result[:start_index] == unencrypted_text
    actual_encrypted_text = actual_anonymize_result[start_index:]
    assert actual_encrypted_text != expected_encrypted_text
    actual_decrypted_text = AESCipher.decrypt(key.encode(), actual_encrypted_text)
    assert actual_decrypted_text == expected_encrypted_text
