from typing import Dict

from presidio_anonymizer.anonymizers import Anonymizer
from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.services.aes_cipher import AESCipher
from presidio_anonymizer.services.validators import validate_parameter


#TODO
class Decrypt(Anonymizer):
    """Restore text to the decrypted form, before it was encrypted."""

    KEY = "key"

    def anonymize(self, text: str = None, params: Dict = None) -> str:
        encoded_key = params.get(self.KEY).encode("utf8")
        decrypted_text = AESCipher.decrypt(key=encoded_key, text=text)
        return decrypted_text

    def validate(self, params: Dict = None) -> None:
        key = params.get(self.KEY)
        validate_parameter(key, self.KEY, str)
        if not AESCipher.is_valid_key_size(key.encode("utf8")):
            raise InvalidParamException(
                f"Invalid input, {self.KEY} must be of length 128, 192 or 256 bits"
            )

    def anonymizer_name(self) -> str:
        """Return anonymizer name."""
        return "decrypt"
