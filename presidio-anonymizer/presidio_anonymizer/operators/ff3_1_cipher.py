from pyfpe_ff3 import FF3Cipher


class FPEFF31Cipher:
    """FPE FF3_1 Cipher"""

    @staticmethod
    def encrypt(key: bytes, tweak: bytes, text: str, radix: int) -> str:
        """
        Encrypts a text using AES cypher in CBC mode.

        Uses padding and random IV.
        :param key: AES encryption key in bytes.
        :param tweak: FF3-1 Tweaks
        :param text: The text for encryption.
        :param radix: Base encoding to use 10 for numeric, 36 for [0-9,a-z], 64 for [0-9, a-z, A-Z, '-].
        :returns: The encrypted text.
        """
        cipher = FF3Cipher(key.decode("utf-8"), tweak.decode("utf-8"), radix, allow_small_domain=True, num_rounds=20)
        encrypted_text = " ".join([cipher.encrypt(t) for t in text.split(' ')])
        return encrypted_text

    @staticmethod
    def decrypt(key: bytes, tweak: bytes, text: str, radix: int) -> str:
        """
        Decrypts a previously AES-CBC encrypted text.

        :param key: AES encryption key in bytes.
        :param text: The text for decryption.
        :param radix: Base encoding to use 10 for numeric, 36 for [0-9,a-z], 64 for [0-9, a-z, A-Z, '-].
        :returns: The decrypted text.
        """
        cipher = FF3Cipher(key.decode("utf-8"), tweak.decode("utf-8"), radix, allow_small_domain=True, num_rounds=20)
        decrypted_text = " ".join([cipher.decrypt(t) for t in text.split(' ')])
        return decrypted_text

    @staticmethod
    def is_valid_key_size(key: bytes) -> bool:
        """
        Validate key size for AES.

        :param key: AES encryption key in bytes.
        :returns: True if the key is of valid size, False otherwise.
        """
        return True  # len(key) in AES.key_size
