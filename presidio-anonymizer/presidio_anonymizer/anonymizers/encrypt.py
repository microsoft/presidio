from typing import Dict

from presidio_anonymizer.anonymizers import Anonymizer
from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.services.aes_cipher import AESCipher
from presidio_anonymizer.services.validators import validate_parameter


class Encrypt(Anonymizer):
    """Anonymizes text to an encrypted form, or it to be restored using decrypted."""

    KEY = "key"

    def anonymize(self, text: str = None, params: Dict = None) -> str:
        """
        Anonymize the text with an encrypted text.

        :param text: The text for encryption.
        :param params:
            * *key* The key supplied by the user for the encryption.
        :return: The encrypted text
        """
        encoded_key = params.get(self.KEY).encode("utf8")
        aes_cipher = AESCipher(encoded_key)
        encrypted_text = aes_cipher.encrypt(text)
        return encrypted_text

    def validate(self, params: Dict = None) -> None:
        """
        Validate Encrypt parameters.

        :param params:
            * *key* The key supplied by the user for the encryption.
                    Should be a string of 128, 192 or 256 bits length.
        :raises: InvalidParamException in case on an invalid parameter.
        """
        key = params.get(self.KEY)
        validate_parameter(key, self.KEY, str)
        if not self._validate_key_length_and_format(key):
            raise InvalidParamException(
                f"Invalid input, {self.KEY} must of length 128, 192 or 256 bits"
            )

    def anonymizer_name(self) -> str:
        """Return   anonymizer name."""
        return "encrypt"

    @staticmethod
    def _validate_key_length_and_format(key):
        return len(key.encode("utf8")) in AESCipher.get_valid_key_sizes()
