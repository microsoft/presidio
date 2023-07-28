from typing import Dict

import base64
from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.operators import Operator
from presidio_anonymizer.operators import OperatorType
from presidio_anonymizer.operators.aes_cipher import AESCipher
from presidio_anonymizer.services.validators import validate_parameter


class Decrypt(Operator):
    """Decrypt text to from its encrypted form."""

    NAME = "decrypt"
    KEY = "key"

    def operate(self, text: str = None, params: Dict = None) -> str:
        """
        Decrypt the text.

        :param text: The text for decryption.
        :param params:
            **key* The key supplied by the user for the encryption
            in a base64 encoded string.
        :return: The encrypted text
        """
        key_bytes = base64.b64decode(params.get(self.KEY), validate=True)
        decrypted_text = AESCipher.decrypt(key=key_bytes, text=text)
        return decrypted_text

    def validate(self, params: Dict = None) -> None:
        """
        Validate Decrypt parameters.

        :param params:
            * *key* The key supplied by the user for the encryption in
            a base64 encoded string. The base64 decoded key should be bytes
            of 128, 192 or 256 bits length.
        :raises InvalidParamException in case on an invalid parameter.
        """
        try:
            key_bytes = base64.b64decode(params.get(self.KEY), validate=True)
        except Exception as e:
            raise InvalidParamException(
                f"Invalid input, {self.KEY} must be base64 encoded"
            ) from e
        validate_parameter(params.get(self.KEY), self.KEY, str)
        if not AESCipher.is_valid_key_size(key_bytes):
            raise InvalidParamException(
                f"Invalid input, {self.KEY} must be of base64 encoded bytes "
                "of length 128, 192 or 256 bits"
            )

    def operator_name(self) -> str:
        """Return operator name."""
        return self.NAME

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Deanonymize
