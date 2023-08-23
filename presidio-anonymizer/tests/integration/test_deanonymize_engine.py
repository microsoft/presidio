import pytest

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.deanonymize_engine import DeanonymizeEngine
from presidio_anonymizer.entities import (
    InvalidParamException,
    RecognizerResult,
    OperatorResult,
    OperatorConfig,
)
from presidio_anonymizer.operators import Decrypt


def test_given_operator_decrypt_with_valid_params_then_decrypt_text_successfully():
    text = "My name is S184CMt9Drj7QaKQ21JTrpYzghnboTF9pn/neN8JME0="
    encryption_results = [
        OperatorResult(start=11, end=55, entity_type="PERSON"),
    ]
    engine = DeanonymizeEngine()
    decryption = engine.deanonymize(
        text,
        encryption_results,
        {"DEFAULT": OperatorConfig(Decrypt.NAME, {"key": b'WmZq4t7w!z%C&F)J'})},
    )
    assert decryption.text == "My name is Chloë"
    assert len(decryption.items) == 1
    assert decryption.items[0].text == "Chloë"
    assert decryption.items[0].end == 16
    assert decryption.items[0].start == 11
    assert decryption.items[0].entity_type == "PERSON"


def test_empty_text_returns_empty_text():
    text = ""
    encryption_results = []
    engine = DeanonymizeEngine()
    decryption = engine.deanonymize(
        text,
        encryption_results,
        {"DEFAULT": OperatorConfig(Decrypt.NAME, {"key": "WmZq4t7w!z%C&F)J"})},
    )

    assert text == decryption.text


def test_given_short_key_then_we_fail():
    text = "My name is S184CMt9Drj7QaKQ21JTrpYzghnboTF9pn/neN8JME0="
    encryption_results = [
        OperatorResult(start=11, end=55, entity_type="PERSON"),
    ]
    engine = DeanonymizeEngine()
    expected_result = "Invalid input, key must be of length 128, 192 or 256 bits"
    with pytest.raises(InvalidParamException, match=expected_result):
        engine.deanonymize(
            text,
            encryption_results,
            {"PERSON": OperatorConfig(Decrypt.NAME, {"key": "1234"})},
        )


def test_given_anonymize_with_encrypt_then_text_returned_with_encrypted_content():
    unencrypted_text = "My name is "
    expected_encrypted_text = "Chloë"
    text = unencrypted_text + expected_encrypted_text
    start_index = 11
    end_index = 16
    key = "WmZq4t7w!z%C&F)J"
    analyzer_results = [RecognizerResult("PERSON", start_index, end_index, 0.8)]
    anonymizers_config = {"PERSON": OperatorConfig("encrypt", {"key": key})}

    actual_anonymize_result = AnonymizerEngine().anonymize(
        text, analyzer_results, anonymizers_config
    )

    assert len(actual_anonymize_result.items) == 1
    anonymized_entities = actual_anonymize_result.items

    engine = DeanonymizeEngine()
    decryption = engine.deanonymize(
        actual_anonymize_result.text,
        anonymized_entities,
        {"PERSON": OperatorConfig(Decrypt.NAME, {"key": key})},
    )
    assert decryption.text == "My name is Chloë"
    assert len(decryption.items) == 1
    assert decryption.items[0].text == "Chloë"
    assert decryption.items[0].end == 16
    assert decryption.items[0].start == 11
    assert decryption.items[0].entity_type == "PERSON"


def test_given_request_deanonymizers_return_list():
    engine = DeanonymizeEngine()
    expected_list = ["decrypt"]
    anon_list = engine.get_deanonymizers()

    assert anon_list == expected_list
