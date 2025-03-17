import re

import pytest

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import (
    InvalidParamError,
    RecognizerResult,
    OperatorConfig,
)
from presidio_anonymizer.operators import AESCipher, OperatorType, Redact
from tests.mock_operators import (
    create_reverser_operator,
    create_instance_counter_anonymizer,
)


def test_given_url_at_the_end_then_we_redact_is_successfully():
    text = "The url is http://microsoft.com"
    anonymizer_config = {
        "URL": OperatorConfig("redact"),
    }

    analyzer_results = [
        RecognizerResult(start=11, end=31, score=1.0, entity_type="URL"),
        RecognizerResult(start=18, end=31, score=1.0, entity_type="URL"),
    ]
    expected_result = (
        '{"text": "The url is ", "items": [{"start": 11, "end": 11, "entity_type": '
        '"URL", "text": "", "operator": "redact"}]}'
    )
    run_engine_and_validate(text, anonymizer_config, analyzer_results, expected_result)


def test_given_operator_decrypt_then_we_fail():
    text = "hello world, my name is Jane Doe. My number is: 03-4453334"
    anonymizers_config = {"DEFAULT": OperatorConfig("decrypt", {"key": "key"})}
    analyzer_results = [
        RecognizerResult(start=24, end=32, score=0.8, entity_type="NAME"),
    ]
    engine = AnonymizerEngine()
    with pytest.raises(
        InvalidParamError,
        match="Invalid operator class 'decrypt'.",
    ):
        engine.anonymize(text, analyzer_results, anonymizers_config)


def test_given_name_and_phone_number_then_we_anonymize_correctly():
    text = "hello world, my name is Jane Doe. My number is: 03-4453334"
    anonymizer_config = {
        "DEFAULT": OperatorConfig(
            "mask", {"masking_char": "*", "chars_to_mask": 20, "from_end": False}
        ),
        "PHONE_NUMBER": OperatorConfig(
            "mask", {"masking_char": "*", "chars_to_mask": 6, "from_end": True}
        ),
    }
    analyzer_results = [
        RecognizerResult(start=24, end=32, score=0.8, entity_type="NAME"),
        RecognizerResult(start=48, end=57, score=0.95, entity_type="PHONE_NUMBER"),
    ]
    expected_result = (
        '{"text": "hello world, my name is ********. My number is: '
        '03-******4", "items": [{"start": 48, "end": 57, "entity_type": '
        '"PHONE_NUMBER", "text": "03-******", "operator": "mask"}, '
        '{"start": 24, "end": 32, "entity_type": "NAME", '
        '"text": "********", "operator": "mask"}]}'
    )
    run_engine_and_validate(text, anonymizer_config, analyzer_results, expected_result)


def test_given_name_and_phone_number_without_anonymizers_then_we_use_default():
    text = "hello world, my name is Jane Doe. My number is: 03-4453334"
    anonymizer_config = {
        "ABC": OperatorConfig(
            "mask", {"masking_char": "*", "chars_to_mask": 6, "from_end": True}
        )
    }
    analyzer_results = [
        RecognizerResult(start=24, end=32, score=0.8, entity_type="NAME"),
        RecognizerResult(start=48, end=57, score=0.95, entity_type="PHONE_NUMBER"),
    ]
    expected_result = (
        '{"text": "hello world, my name is <NAME>. My number is: '
        '<PHONE_NUMBER>4", "items": [{"start": 46, "end": 60, '
        '"entity_type": "PHONE_NUMBER", "text": "<PHONE_NUMBER>", '
        '"operator": "replace"}, {"start": 24, "end": 30, '
        '"entity_type": "NAME", "text": "<NAME>", '
        '"operator": "replace"}]}'
    )
    run_engine_and_validate(text, anonymizer_config, analyzer_results, expected_result)


def test_given_redact_and_replace_then_we_anonymize_successfully():
    text = "hello world, my name is Jane Doe. My number is: 03-4453334"
    anonymizer_config = {
        "NAME": OperatorConfig("redact", {"new_value": "ANONYMIZED"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": ""}),
    }
    analyzer_results = [
        RecognizerResult(start=24, end=32, score=0.8, entity_type="NAME"),
        RecognizerResult(start=48, end=57, score=0.95, entity_type="PHONE_NUMBER"),
    ]
    expected_result = (
        '{"text": "hello world, my name is . My number is: '
        '<PHONE_NUMBER>4", "items": [{"start": 40, "end": 54, '
        '"entity_type": "PHONE_NUMBER", "text": "<PHONE_NUMBER>", '
        '"operator": "replace"}, {"start": 24, "end": 24, '
        '"entity_type": "NAME", "text": "", "operator": '
        '"redact"}]}'
    )
    run_engine_and_validate(text, anonymizer_config, analyzer_results, expected_result)


def test_given_intersecting_entities_then_we_anonymize_correctly():
    text = "hello world, my name is Jane Doe. My number is: 03-4453334"
    anonymizer_config = {}
    analyzer_results = [
        RecognizerResult(start=24, end=32, score=0.6, entity_type="FULL_NAME"),
        RecognizerResult(start=48, end=56, score=0.95, entity_type="PHONE_NUMBER"),
        RecognizerResult(start=54, end=57, score=0.8, entity_type="SSN"),
        RecognizerResult(start=24, end=28, score=0.9, entity_type="FIRST_NAME"),
        RecognizerResult(start=29, end=33, score=0.6, entity_type="LAST_NAME"),
        RecognizerResult(start=24, end=30, score=0.8, entity_type="NAME"),
    ]
    expected_result = (
        '{"text": "hello world, my name is <FULL_NAME><LAST_NAME> My '
        'number is: <PHONE_NUMBER><SSN>4", "items": [{"start": 75, '
        '"end": 80, "entity_type": "SSN", "text": "<SSN>", '
        '"operator": "replace"}, {"start": 61, "end": 75, '
        '"entity_type": "PHONE_NUMBER", "text": "<PHONE_NUMBER>", '
        '"operator": "replace"}, {"start": 35, "end": 46, '
        '"entity_type": "LAST_NAME", "text": "<LAST_NAME>", '
        '"operator": "replace"}, {"start": 24, "end": 35, '
        '"entity_type": "FULL_NAME", "text": "<FULL_NAME>", '
        '"operator": "replace"}]}'
    )
    run_engine_and_validate(text, anonymizer_config, analyzer_results, expected_result)


def test_given_intersecting_the_same_entities_then_we_anonymize_correctly():
    text = "hello world, my name is Jane Doe. My number is: 03-4453334"
    anonymizer_config = {}
    analyzer_results = [
        RecognizerResult(start=24, end=32, score=0.6, entity_type="FULL_NAME"),
        RecognizerResult(start=29, end=33, score=0.6, entity_type="FULL_NAME"),
    ]
    expected_result = (
        '{"text": "hello world, my name is <FULL_NAME> My number is: 03-4453334", '
        '"items": [{"start": 24, "end": 35, "entity_type": "FULL_NAME",'
        ' "text": "<FULL_NAME>", "operator": "replace"}]}'
    )
    run_engine_and_validate(text, anonymizer_config, analyzer_results, expected_result)


@pytest.mark.parametrize(
    # fmt: off
    "hash_type,result",
    [
        ("sha256",
         '{"text": "hello world, my name is '
         '01332c876518a793b7c1b8dfaf6d4b404ff5db09b21c6627ca59710cc24f696a. '
         'My number is: 230451ebc7df208f1d5227aceaebf6d8e9'
         '36f17d74330a5a5c5cbbd4e41d0d57", "items": [{"start": 104, "end": 168, '
         '"entity_type": "PHONE_NUMBER", "text": "230451ebc7df208f1d5227aceaebf6d8e'
         '936f17d74330a5a5c5cbbd4e41d0d57", "operator": "hash"}, {"start": 24, '
         '"end": 88, "entity_type": "NAME", "text": "01332c876518a793b7c1b8dfaf6d4b404f'
         'f5db09b21c6627ca59710cc24f696a", "operator": "hash"}]}'),
        ("sha512",
         '{"text": "hello world, my name is 508789e7c17beebf2f17e611b43920792b692a'
         'd9ae53f9be3a947b04fbf820f40d57f42864a20e7121180e9467fda3fa2480e50c0da15244b'
         '6153abe2509362c. My number is: 8ea244bbf71264237db23324b3ff83f6ef6601c9da08a'
         'f42122f992ec45d757c3efd953185b2590e4542aa1ca3637fa8935ebff2b43af0ea1245e7c84'
         '3fbebdc", "items": [{"start": 168, "end": 296, "entity_type": "PHONE_NUMBER",'
         ' "text": "8ea244bbf71264237db23324b3ff83f6ef6601c9da08af42122f992ec45d757c'
         '3efd953185b2590e4542aa1ca3637fa8935ebff2b43af0ea1245e7c843fbebdc", '
         '"operator": "hash"}, {"start": 24, "end": 152, "entity_type": "NAME", '
         '"text": "508789e7c17beebf2f17e611b43920792b692ad9ae53f9be3a947b04fbf820f40'
         'd57f42864a20e7121180e9467fda3fa2480e50c0da15244b6153abe2509362c", '
         '"operator": "hash"}]}'),
        ("",
         '{"text": "hello world, my name is 01332c876518a793b7c1b8dfaf6d4b404ff5db09b'
         '21c6627ca59710cc24f696a. My number is: 230451ebc7df208f1d5227aceaebf6d8e936f'
         '17d74330a5a5c5cbbd4e41d0d57", "items": [{"start": 104, "end": 168, '
         '"entity_type": "PHONE_NUMBER", "text": "230451ebc7df208f1d5227aceaebf6d8e936'
         'f17d74330a5a5c5cbbd4e41d0d57", "operator": "hash"}, {"start": 24, '
         '"end": 88, "entity_type": "NAME", "text": "01332c876518a793b7c1b8dfaf6d4b404'
         'ff5db09b21c6627ca59710cc24f696a", "operator": "hash"}]}'
         )
    ],
    # fmt: on
)
def test_given_hash_then_we_anonymize_correctly(hash_type, result):
    text = "hello world, my name is Jane Doe. My number is: 034453334"
    params = {}
    if hash_type:
        params = {"hash_type": hash_type}
    anonymizer_config = {"DEFAULT": OperatorConfig("hash", params)}
    analyzer_results = [
        RecognizerResult(start=48, end=57, score=0.95, entity_type="PHONE_NUMBER"),
        RecognizerResult(start=24, end=28, score=0.8, entity_type="FIRST_NAME"),
        RecognizerResult(start=29, end=32, score=0.6, entity_type="LAST_NAME"),
        RecognizerResult(start=24, end=32, score=0.8, entity_type="NAME"),
    ]
    run_engine_and_validate(text, anonymizer_config, analyzer_results, result)


def run_engine_and_validate(
    text: str, anonymizers_config, analyzer_results, expected_result
):
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
        "PHONE_NUMBER": OperatorConfig(
            "mask",
            {"masking_char": "non_character", "chars_to_mask": 6, "from_end": True},
        )
    }
    analyzer_results = [RecognizerResult("PHONE_NUMBER", 48, 57, 0.95)]

    engine = AnonymizerEngine()

    try:
        actual_anonymize_result = engine.anonymize(text, analyzer_results, anonymizers)
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
    anonymizers_config = {"PERSON": OperatorConfig("encrypt", {"key": key})}

    actual_anonymize_result = (
        AnonymizerEngine().anonymize(text, analyzer_results, anonymizers_config).text
    )

    assert actual_anonymize_result[:start_index] == unencrypted_text
    actual_encrypted_text = actual_anonymize_result[start_index:]
    assert actual_encrypted_text != expected_encrypted_text
    actual_decrypted_text = AESCipher.decrypt(key.encode(), actual_encrypted_text)
    assert actual_decrypted_text == expected_encrypted_text


def test_empty_text_returns_correct_results():
    text = ""
    analyzer_results = []

    actual_anonymize_result = AnonymizerEngine().anonymize(text, analyzer_results)

    assert actual_anonymize_result.text == text


def test_add_anonymizer_returns_updated_list(mock_anonymizer_cls):
    engine = AnonymizerEngine()
    anon_list_len = len(engine.get_anonymizers())
    engine.add_anonymizer(mock_anonymizer_cls)
    anon_list = engine.get_anonymizers()
    assert len(anon_list) == anon_list_len + 1
    assert mock_anonymizer_cls().operator_name() in anon_list


def test_anonymizer_engine_uses_custom_operator():
    engine = AnonymizerEngine()
    engine.add_anonymizer(create_reverser_operator(OperatorType.Anonymize))
    text = "hello"
    analyzer_results = [RecognizerResult("WORD", 0, 5, 1.0)]

    actual_anonymize_result = engine.anonymize(
        text, analyzer_results, {"WORD": OperatorConfig("Reverser")}
    )
    assert actual_anonymize_result.text == "hello"[::-1]


def test_remove_anonymizer_removes_anonymizer():
    engine = AnonymizerEngine()
    num_of_anonymizers = len(engine.get_anonymizers())
    engine.remove_anonymizer(Redact)
    anonymizers = engine.get_anonymizers()
    assert len(anonymizers) == num_of_anonymizers - 1


def test_operator_metadata_returns_updated_results(three_person_analyzer_results):
    counter_anonymizer = create_instance_counter_anonymizer()
    engine = AnonymizerEngine()
    engine.add_anonymizer(counter_anonymizer)
    text, analyzer_results = three_person_analyzer_results

    entity_mapping = dict()

    actual_anonymize_result = engine.anonymize(
        text,
        analyzer_results,
        {
            "DEFAULT": OperatorConfig(
                "entity_counter", {"entity_mapping": entity_mapping}

            )
        },
    )

    pattern = r'<PERSON_\d+>'
    assert len(re.findall(pattern, actual_anonymize_result.text)) == 3
    for results in actual_anonymize_result.items:
        assert results.operator == "entity_counter"
        assert results.entity_type == "PERSON"
        assert re.findall(pattern, results.text)
