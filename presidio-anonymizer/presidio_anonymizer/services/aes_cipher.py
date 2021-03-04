from typing import Tuple

from Crypto.Util.Padding import pad, unpad

import base64
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher:
    """Advanced Encryption Standard (aka Rijndael) en/decryption in CBC mode."""

    def __init__(self, key: bytes) -> None:
        """
        Instantiate AESCipher.

        :param key: AES key in bytes
        """
        self.key = key

    def encrypt(self, text: str) -> str:
        """
        Encrypts a text using AES cypher in CBC mode.

        Uses padding and random IV.
        :param text: The text for encryption.
        :returns: The encrypted text.
        """
        encoded_text = text.encode("utf-8")
        padded_text = pad(encoded_text, AES.block_size)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted_text = base64.b64encode(iv + cipher.encrypt(padded_text))
        return encrypted_text.decode()

    def decrypt(self, text: str) -> str:
        """
        Decrypts a previously AES-CBC encrypted text.

        :param text: The text for decryption.
        :returns: The decrypted text.
        """
        decoded_text = base64.b64decode(text)
        iv = decoded_text[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_text = unpad(
            cipher.decrypt(decoded_text[AES.block_size :]), AES.block_size
        )
        return decrypted_text.decode("utf-8")

    @staticmethod
    def get_valid_key_sizes() -> Tuple[int, ...]:
        """
        Get the valid key size for AES.

        :returns: A tuple of valid key sizes.
        """
        return AES.key_size
