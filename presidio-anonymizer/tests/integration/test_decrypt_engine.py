import pytest

from presidio_anonymizer import DecryptEngine
from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.engine import EncryptResult


def test_given_operator_decrypt_with_valid_params_then_we_decrypt_text_successfully():
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
