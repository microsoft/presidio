import os

import pytest

from presidio_anonymizer.operators import AESCipher


@pytest.mark.parametrize(
    # fmt: off
    "key,text",
    [
        (b'1111111111111111', "text_for_encryption"),  # 16 bits key
        (b'111111111111111111111111', "text_for_encryption"),  # 24 bits key
        (b'11111111111111111111111111111111', "text_for_encryption"),  # 32 bits key
        (b'1111111111111111', "PII with a Résumé"),  # Text with e-acute
        (b'1111111111111111', "面汤"),  # Chinese text
        (b'1111111111111111', "הצפן אותי"),  # Hebrew text
        (b'1111111111111111', "😈😈😈😈"),  # Text with EmojiSources character
        (os.urandom(16), "text_for_encryption"),   # random 16 bits key
    ],
    # fmt: on
)
def test_given_valid_key_and_text_then_text_encryption_and_decryption_returns_same_text(
    key, text
):
    encrypted_text = AESCipher.encrypt(key, text)

    decrypted_text = AESCipher.decrypt(key, encrypted_text)
    assert text == decrypted_text


def test_given_invalid_key_length_then_value_error_raised():
    invalid_length_key = b"1111"
    with pytest.raises(ValueError, match="Invalid key size \(32\) for AES"):
        AESCipher.encrypt(invalid_length_key, "text")


@pytest.mark.parametrize(
    # fmt: off
    "key,is_valid",
    [
        (b'', False),  # Empty bit-string key
        (b'1111111111111111', True),  # 16 bits key
        (b'11111111111111111', False),  # 17 bits key
        (b'111111111111111111111111', True),  # 24 bits key
        (b'1111111111111111111111111', False),  # 25 bits key
        (b'11111111111111111111111111111111', True),  # 32 bits key
        (b'111111111111111111111111111111111', False),  # 33 bits key
        (os.urandom(16), True),  # random 16 bits key
    ],
    # fmt: on
)
def test_given_is_valid_key_size_called_then_aes_valid_key_sizes_returned(
    key, is_valid
):
    assert AESCipher.is_valid_key_size(key) == is_valid
