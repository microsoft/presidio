from typing import Dict

from presidio_anonymizer.operators import Encrypt, Operator, OperatorType
from presidio_anonymizer.operators.aes_cipher import AESCipher


class Decrypt(Operator):
    """Decrypt text to from its encrypted form."""

    NAME = "decrypt"
    KEY = "key"

    def operate(self, text: str = None, params: Dict = None) -> str:
        """
        Decrypt the text.

        :param text: The text for decryption.
        :param params:
            **key* The key supplied by the user for the encryption (bytes or str).
        :return: The encrypted text
        """
        key = params.get(self.KEY)
        if isinstance(key, str):
            key = key.encode("utf8")
        decrypted_text = AESCipher.decrypt(key=key, text=text)
        return decrypted_text

    def validate(self, params: Dict = None) -> None:
        """
        Validate Decrypt parameters.

        :param params:
            * *key* The key supplied by the user for the encryption.
                    Should be a string of 128, 192 or 256 bits length.
        :raises InvalidParamException: in case on an invalid parameter.
        """
        Encrypt().validate(params)

    def operator_name(self) -> str:
        """Return operator name."""
        return self.NAME

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Deanonymize
