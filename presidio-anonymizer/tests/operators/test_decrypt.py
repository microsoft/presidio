from unittest import mock

import pytest

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.operators import Decrypt
from presidio_anonymizer.operators.aes_cipher import AESCipher
from presidio_anonymizer.operators.ff3_1_cipher import FPEFF31Cipher


@mock.patch.object(AESCipher, "decrypt")
def test_given_anonymize_then_aes_encrypt_called_and_its_result_is_returned(
        mock_encrypt,
):
    expected_decrypted_text = "decrypted_text"
    mock_encrypt.return_value = expected_decrypted_text

    anonymized_text = Decrypt().operate(text="text", params={"key": "key"})

    assert anonymized_text == expected_decrypted_text


def test_given_verifying_an_valid_length_key_no_exceptions_raised():
    Decrypt().validate(params={"key": "128bitslengthkey"})


def test_given_verifying_an_invalid_length_key_then_ipe_raised():
    with pytest.raises(
            InvalidParamException,
            match="Invalid input, key must be of length 128, 192 or 256 bits",
    ):
        Decrypt().validate(params={"key": "key"})


@mock.patch.object(FPEFF31Cipher, "decrypt")
def test_given_deanonymize_using_ff3_encrypt_and_its_result_is_matched(
    mock_encrypt,
):
    expected_deanonymized_text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456B",
    mock_encrypt.return_value = expected_deanonymized_text
    deanonymized_text = Decrypt().operate(text="svexCluwcMujPeWF1iZe2rniKJNYR9noT",
                                          params={
                                              "encryption": "FPEFF31",
                                              "radix": 64,
                                              "key": "EF4359D8D580AA4F7F036D6F04FC6A94",
                                              "tweak": "D8E7920AFA330A73",
                                              "allow_small_domain": True})

    assert deanonymized_text == expected_deanonymized_text
