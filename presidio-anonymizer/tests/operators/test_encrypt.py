from unittest import mock

import pytest

from presidio_anonymizer.operators.encrypt import Encrypt
from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.operators.aes_cipher import AESCipher
from presidio_anonymizer.operators.ff3_1_cipher import FPEFF31Cipher

@mock.patch.object(AESCipher, "encrypt")
def test_given_anonymize_then_aes_encrypt_called_and_its_result_is_returned(
    mock_encrypt,
):
    expected_anonymized_text = "encrypted_text"
    mock_encrypt.return_value = expected_anonymized_text

    anonymized_text = Encrypt().operate(text="text", params={"key": "key"})

    assert anonymized_text == expected_anonymized_text


def test_given_verifying_an_valid_length_key_no_exceptions_raised():
    Encrypt().validate(params={"key": "128bitslengthkey"})


def test_given_verifying_an_invalid_length_key_then_ipe_raised():
    with pytest.raises(
        InvalidParamException,
        match="Invalid input, key must be of length 128, 192 or 256 bits",
    ):
        Encrypt().validate(params={"key": "key"})


@mock.patch.object(FPEFF31Cipher, "encrypt")
def test_given_anonymize_using_ff3_encrypt_and_its_result_is_matched(
    mock_encrypt,
):
    expected_anonymized_text = "svexCluwcMujPeWF1iZe2rniKJNYR9noT",
    mock_encrypt.return_value = expected_anonymized_text
    anonymized_text = Encrypt().operate(text="ABCDEFGHIJKLMNOPQRSTUVWXYZ123456B", params={
        "encryption": "FPEFF31",
        "radix": 64,
        "key": "EF4359D8D580AA4F7F036D6F04FC6A94",
        "tweak": "D8E7920AFA330A73",
        "allow_small_domain": True})

    assert anonymized_text == expected_anonymized_text

