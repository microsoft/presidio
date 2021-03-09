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
        encrypted_text = AESCipher.encrypt(encoded_key, text)
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
        if not AESCipher.is_valid_key_size(key.encode("utf8")):
            raise InvalidParamException(
                f"Invalid input, {self.KEY} must be of length 128, 192 or 256 bits"
            )

    def anonymizer_name(self) -> str:
        """Return anonymizer name."""
        return "encrypt"
