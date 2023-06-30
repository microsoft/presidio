import pytest

from presidio_anonymizer.deanonymize_engine import DeanonymizeEngine
from presidio_anonymizer.anonymizer_engine import  AnonymizerEngine
from presidio_anonymizer.entities import (
    InvalidParamException,
    RecognizerResult,
    OperatorResult,
    OperatorConfig,
)
from presidio_anonymizer.operators import Decrypt, AESCipher, OperatorsFactory, OperatorType
from tests.operators.mock_operators_utils import setup_function, teardown_function, resetOperatorsFactory, custom_indirect_operator



def test_given_operator_decrypt_with_valid_params_then_decrypt_text_successfully():
    text = "My name is S184CMt9Drj7QaKQ21JTrpYzghnboTF9pn/neN8JME0="
    encryption_results = [
        OperatorResult(start=11, end=55, entity_type="PERSON"),
    ]
    engine = DeanonymizeEngine()
    decryption = engine.deanonymize(
        text,
        encryption_results,
        {"DEFAULT": OperatorConfig(Decrypt.NAME, {"key": "WmZq4t7w!z%C&F)J"})},
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
    expected_list = ["decrypt", "decrypt2", "decrypt3"]
    anon_list = engine.get_deanonymizers()

    assert anon_list == expected_list

def test_given_deanonymize_operators_class_then_we_get_the_correct_class():

    for operator_name in ["decrypt", "decrypt3", "decrypt2"]:
        resetOperatorsFactory()
        if operator_name == "decrypt3":
            #decrypt3 inherits Operator directly
            from tests.operators.mock_operators import Decrypt3
        if operator_name == "decrypt2":
            #decrypt2 inherits Operator inderactely
            #first lets unload Decrypt3
            del Decrypt3
            #now, lets import Decrypt2
            from tests.operators.mock_operators import Decrypt2



        operator = OperatorsFactory().create_operator_class(
            operator_name, OperatorType.Deanonymize
        )
        assert operator
        assert operator.operator_name() == operator_name
        assert (
            operator.operator_type() == OperatorType.Deanonymize
            or operator.operator_type() == OperatorType.All
        )
    resetOperatorsFactory()
    del Decrypt2


def test_given_anonymize_operators_class_then_we_get_the_correct_class():
    for operator_name in ["hash", "mask", "redact", "replace", "encrypt", "custom",
                           "encrypt3", "encrypt2"]:
        resetOperatorsFactory()
        if operator_name == "encrypt3":
            #encrypt3 inherits Operator directly
            from tests.operators.mock_operators import Encrypt3
        if operator_name == "encrypt2":
            #encrypt2 inherits Operator inderactely
            #first lets unload Encrypt3
            del Encrypt3
            #now, lets import Encrypt2
            from tests.operators.mock_operators import Encrypt2



        operator = OperatorsFactory().create_operator_class(
            operator_name, OperatorType.Anonymize
        )
        assert operator
        assert operator.operator_name() == operator_name
        assert (
            operator.operator_type() == OperatorType.Anonymize
            or operator.operator_type() == OperatorType.All
        )

    resetOperatorsFactory()
    del Encrypt2