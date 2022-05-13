import base64

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


class AESCipher:
    """Advanced Encryption Standard (aka Rijndael) en/decryption in CBC mode."""

    @staticmethod
    def encrypt(key: bytes, text: str) -> str:
        """
        Encrypts a text using AES cypher in CBC mode.

        Uses padding and random IV.
        :param key: AES encryption key in bytes.
        :param text: The text for encryption.
        :returns: The encrypted text.
        """
        encoded_text = text.encode("utf-8")
        padded_text = pad(encoded_text, AES.block_size)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_text = base64.b64encode(iv + cipher.encrypt(padded_text))
        return encrypted_text.decode()

    @staticmethod
    def decrypt(key: bytes, text: str) -> str:
        """
        Decrypts a previously AES-CBC encrypted text.

        :param key: AES encryption key in bytes.
        :param text: The text for decryption.
        :returns: The decrypted text.
        """
        decoded_text = base64.b64decode(text)
        iv = decoded_text[: AES.block_size]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_text = unpad(
            cipher.decrypt(decoded_text[AES.block_size :]), AES.block_size
        )
        return decrypted_text.decode("utf-8")

    @staticmethod
    def is_valid_key_size(key: bytes) -> bool:
        """
        Validate key size for AES.

        :param key: AES encryption key in bytes.
        :returns: True if the key is of valid size, False otherwise.
        """
        return len(key) in AES.key_size
