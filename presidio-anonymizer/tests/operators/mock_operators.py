from typing import Dict

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.operators import Operator, OperatorType, Encrypt, Decrypt
from presidio_anonymizer.operators.aes_cipher import AESCipher
from presidio_anonymizer.services.validators import validate_parameter


class Encrypt2(Encrypt):

    def operate(self, text: str = None, params: Dict = None) -> str:
        encrypted_text = super().operate(text, params)
        return f"@@@{encrypted_text}@@@"

    def operator_name(self) -> str:
        """Return operator name."""
        return "encrypt2"



class Encrypt3(Operator):
    KEY = "key"

    def operate(self, text: str = None, params: Dict = None) -> str:
        encoded_key = params.get(self.KEY).encode("utf8")
        encrypted_text = AESCipher.encrypt(encoded_key, text)
        return f"@@@{encrypted_text}@@@"

    def validate(self, params: Dict = None) -> None:
        """
        Validate Encrypt parameters.

        :param params:
            * *key* The key supplied by the user for the encryption.
                    Should be a string of 128, 192 or 256 bits length.
        :raises InvalidParamException in case on an invalid parameter.
        """
        key = params.get(self.KEY)
        validate_parameter(key, self.KEY, str)
        if not AESCipher.is_valid_key_size(key.encode("utf8")):
            raise InvalidParamException(
                f"Invalid input, {self.KEY} must be of length 128, 192 or 256 bits"
            )

    def operator_name(self) -> str:
        """Return operator name."""
        return "encrypt3"

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Anonymize


class Decrypt2(Decrypt):
    """Decrypt text to from its encrypted form."""

    NAME = "decrypt2"
    PATTERN = r'@@@([\w\s\\]+)@@@'  # r'@@@(.*?)@@@' #

    def operate(self, text: str = None, params: Dict = None) -> str:
        """
        Decrypt the text.

        :param text: The text for decryption.
        :param params:
            **key* The key supplied by the user for the encryption.
        :return: The encrypted text
        """
        text = text.removeprefix('@@@')
        text = text.removesuffix('@@@')
        decrypted_text = super().operate(text, params)
        return decrypted_text


class Decrypt3(Operator):
    """Decrypt text to from its encrypted form."""

    NAME = "decrypt3"
    KEY = "key"
    PATTERN = r'@@@([\w\s\\]+)@@@'  # r'@@@(.*?)@@@' #

    def operate(self, text: str = None, params: Dict = None) -> str:
        """
        Decrypt the text.

        :param text: The text for decryption.
        :param params:
            **key* The key supplied by the user for the encryption.
        :return: The encrypted text
        """
        encoded_key = params.get(self.KEY).encode("utf8")
        text=text.removeprefix('@@@')
        text=text.removesuffix('@@@')
        decrypted_text = AESCipher.decrypt(key=encoded_key, text=text)
        return decrypted_text

    def validate(self, params: Dict = None) -> None:
        """
        Validate Decrypt parameters.

        :param params:
            * *key* The key supplied by the user for the encryption.
                    Should be a string of 128, 192 or 256 bits length.
        :raises InvalidParamException in case on an invalid parameter.
        """
        key = params.get(self.KEY)
        validate_parameter(key, self.KEY, str)
        if not AESCipher.is_valid_key_size(key.encode("utf8")):
            raise InvalidParamException(
                f"Invalid input, {self.KEY} must be of length 128, 192 or 256 bits"
            )

    def operator_name(self) -> str:
        """Return operator name."""
        return self.NAME

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Deanonymize
