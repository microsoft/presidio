from unittest import mock
import base64
import pytest

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.operators import Decrypt, AESCipher


@mock.patch.object(AESCipher, "decrypt")
def test_given_anonymize_then_aes_encrypt_called_and_its_result_is_returned(
    mock_encrypt,
):
    expected_decrypted_text = "decrypted_text"
    mock_encrypt.return_value = expected_decrypted_text

    base64_encoded_key = base64.b64encode(b"key").decode("utf-8")
    anonymized_text = Decrypt().operate(text="text", params={"key": base64_encoded_key})

    assert anonymized_text == expected_decrypted_text


def test_given_verifying_an_valid_length_key_no_exceptions_raised():
    base64_encoded_key = base64.b64encode(b"128bitslengthkey").decode("utf-8")
    Decrypt().validate(params={"key": base64_encoded_key})


def test_given_verifying_an_invalid_length_key_then_ipe_raised():
    with pytest.raises(
        InvalidParamException,
        match="Invalid input, key must be of base64 encoded bytes of length 128, 192 or 256 bits",
    ):
        base64_encoded_key = base64.b64encode(b"key").decode("utf-8")
        Decrypt().validate(params={"key": base64_encoded_key})
