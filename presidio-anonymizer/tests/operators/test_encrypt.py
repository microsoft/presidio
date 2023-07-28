from unittest import mock
import base64
import pytest

from presidio_anonymizer.operators import Encrypt, AESCipher
from presidio_anonymizer.entities import InvalidParamException


@mock.patch.object(AESCipher, "encrypt")
def test_given_anonymize_then_aes_encrypt_called_and_its_result_is_returned(
    mock_encrypt,
):
    expected_anonymized_text = "encrypted_text"
    mock_encrypt.return_value = expected_anonymized_text

    base64_encoded_key = base64.b64encode(b"key").decode("utf-8")
    anonymized_text = Encrypt().operate(text="text", params={"key": base64_encoded_key})

    assert anonymized_text == expected_anonymized_text


def test_given_verifying_an_valid_length_key_no_exceptions_raised():
    base64_encoded_key = base64.b64encode(b"128bitslengthkey").decode("utf-8")
    Encrypt().validate(params={"key": base64_encoded_key})


def test_given_verifying_an_invalid_length_key_then_ipe_raised():
    with pytest.raises(
        InvalidParamException,
        match="Invalid input, key must be of base64 encoded bytes of length 128, 192 or 256 bits",
    ):
        base64_encoded_key = base64.b64encode(b"key").decode("utf-8")
        Encrypt().validate(params={"key": base64_encoded_key})
