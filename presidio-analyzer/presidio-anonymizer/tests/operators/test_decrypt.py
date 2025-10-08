from unittest import mock

import pytest

from presidio_anonymizer.entities import InvalidParamError
from presidio_anonymizer.operators import Decrypt, AESCipher


@mock.patch.object(AESCipher, "decrypt")
def test_given_anonymize_then_aes_encrypt_called_and_its_result_is_returned(
    mock_encrypt,
):
    expected_decrypted_text = "decrypted_text"
    mock_encrypt.return_value = expected_decrypted_text

    anonymized_text = Decrypt().operate(text="text", params={"key": "key"})

    assert anonymized_text == expected_decrypted_text


@mock.patch.object(AESCipher, "decrypt")
def test_given_anonymize_with_bytes_key_then_aes_encrypt_result_is_returned(
        mock_encrypt,
):
    expected_decrypted_text = "decrypted_text"
    mock_encrypt.return_value = expected_decrypted_text

    anonymized_text = Decrypt().operate(text="text",
                                        params={"key":  b'1111111111111111'})

    assert anonymized_text == expected_decrypted_text


def test_given_verifying_an_valid_length_key_no_exceptions_raised():
    Decrypt().validate(params={"key": "128bitslengthkey"})


def test_given_verifying_an_valid_length_bytes_key_no_exceptions_raised():
    Decrypt().validate(params={"key": b'1111111111111111'})


def test_given_verifying_an_invalid_length_key_then_ipe_raised():
    with pytest.raises(
        InvalidParamError,
        match="Invalid input, key must be of length 128, 192 or 256 bits",
    ):
        Decrypt().validate(params={"key": "key"})
