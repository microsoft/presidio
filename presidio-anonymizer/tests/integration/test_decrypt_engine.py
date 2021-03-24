import pytest

from presidio_anonymizer import DecryptEngine, AnonymizerEngine
from presidio_anonymizer.entities import InvalidParamException, AnonymizerConfig, \
    RecognizerResult
from presidio_anonymizer.entities.engine import EncryptResult


def test_given_operator_decrypt_with_valid_params_then_decrypt_text_successfully():
    text = "My name is S184CMt9Drj7QaKQ21JTrpYzghnboTF9pn/neN8JME0="
    encryption_results = [
        EncryptResult(
            key="WmZq4t7w!z%C&F)J",
            start=11,
            end=55,
            entity_type="PERSON"
        ),
    ]
    engine = DecryptEngine()
    decryption = engine.decrypt(
        text, encryption_results
    )
    assert decryption.text == "My name is Chloë"
    assert len(decryption.items) == 1
    assert decryption.items[0].decrypted_text == "Chloë"
    assert decryption.items[0].end == 16
    assert decryption.items[0].start == 11
    assert decryption.items[0].entity_type == "PERSON"


def test_given_short_key_then_we_fail():
    text = "My name is S184CMt9Drj7QaKQ21JTrpYzghnboTF9pn/neN8JME0="
    encryption_results = [
        EncryptResult(
            key="123",
            start=11,
            end=55,
            entity_type="PERSON"
        ),
    ]
    engine = DecryptEngine()
    expected_result = "Invalid input, key must be of length 128, 192 or 256 bits"
    with pytest.raises(InvalidParamException,
                       match=expected_result):
        engine.decrypt(
            text, encryption_results
        )


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
        AnonymizerEngine().anonymize(text, analyzer_results, anonymizers_config)
    )

    assert len(actual_anonymize_result.items) == 1
    encryption_results = [
        EncryptResult.from_anonymized_entity(key, actual_anonymize_result.items[0])
    ]
    engine = DecryptEngine()
    decryption = engine.decrypt(
        actual_anonymize_result.text, encryption_results
    )
    assert decryption.text == "My name is Chloë"
    assert len(decryption.items) == 1
    assert decryption.items[0].decrypted_text == "Chloë"
    assert decryption.items[0].end == 16
    assert decryption.items[0].start == 11
    assert decryption.items[0].entity_type == "PERSON"
