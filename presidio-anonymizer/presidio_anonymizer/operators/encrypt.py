from typing import Dict

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.operators import Operator, OperatorType
from presidio_anonymizer.operators.aes_cipher import AESCipher
from presidio_anonymizer.services.validators import validate_parameter


class Encrypt(Operator):
    """Anonymizes text to an encrypted form, or it to be restored using decrypted."""

    KEY = "key"

    def operate(self, text: str = None, params: Dict = None) -> str:
        """
        Anonymize the text with an encrypted text.

        :param text: The text for encryption.
        :param params:
            * *key* The key supplied by the user for the encryption (bytes or str).
        :return: The encrypted text
        """
        key = params.get(self.KEY)
        if type(key) is str:
            key = key.encode("utf8")
        encrypted_text = AESCipher.encrypt(key, text)
        return encrypted_text

    def validate(self, params: Dict = None) -> None:
        """
        Validate Encrypt parameters.

        :param params:
            * *key* The key supplied by the user for the encryption.
                    Should be a string of 128, 192 or 256 bits length.
        :raises InvalidParamException in case on an invalid parameter.
        """
        key = params.get(self.KEY)
        if type(key) is str:
            validate_parameter(key, self.KEY, str)
            if not AESCipher.is_valid_key_size(key.encode("utf8")):
                raise InvalidParamException(
                    f"Invalid input, {self.KEY} must be of length 128, 192 or 256 bits"
                )
        else:
            validate_parameter(key, self.KEY, bytes)
        if not AESCipher.is_valid_key_size(key):
            raise InvalidParamException(
                f"Invalid input, {self.KEY} must be of length 128, 192 or 256 bits"
            )

    def operator_name(self) -> str:
        """Return operator name."""
        return "encrypt"

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Anonymize
