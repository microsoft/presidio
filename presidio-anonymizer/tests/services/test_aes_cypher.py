import pytest

from presidio_anonymizer.services.aes_cipher import AESCipher


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
    with pytest.raises(ValueError, match="Incorrect AES key length"):
        AESCipher.encrypt(invalid_length_key, "text")


def test_given_get_valid_key_sizes_called_then_aes_valid_key_sizes_returned():
    assert AESCipher.get_valid_key_sizes() == (16, 24, 32)
