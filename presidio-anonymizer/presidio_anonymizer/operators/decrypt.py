from typing import Dict

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.operators import Operator
from presidio_anonymizer.operators import OperatorType
from presidio_anonymizer.operators.aes_cipher import AESCipher
from presidio_anonymizer.services.validators import validate_parameter
from presidio_anonymizer.operators.ff3_1_cipher import FPEFF31Cipher


class Decrypt(Operator):
    """Decrypt text to from its encrypted form."""

    NAME = "decrypt"
    KEY = "key"
    ENCRYPTION_METHOD = "encryption"
    FPE_TWEAK = "tweak"
    RADIX = "radix"

    def operate(self, text: str = None, params: Dict = None) -> str:
        """
        Decrypt the text.

        :param text: The text for decryption.
        :param params:
            **key* The key supplied by the user for the encryption.
        :return: The encrypted text
        """
        encoded_key = params.get(self.KEY).encode("utf8")
        encryption_method = params.get(self.ENCRYPTION_METHOD)
        radix = params.get(self.RADIX, 64)
        decrypted_text = None
        if encryption_method == "FPEFF31":
            fpe_tweak = params.get(self.FPE_TWEAK).encode("utf8")
            decrypted_text = FPEFF31Cipher.decrypt(encoded_key, fpe_tweak, text, radix)
        else:
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
