import logging
from typing import List

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.engine.decrypt_config import DecryptConfig
from presidio_anonymizer.entities.engine.encrypt_result import EncryptResult
from presidio_anonymizer.entities.engine.result.engine_result import EngineResult
from presidio_anonymizer.services.aes_cipher import AESCipher
from presidio_anonymizer.services.validators import validate_parameter
from presidio_anonymizer.text_engine import TextEngine


class DecryptEngine:
    """Decrypting text that was previously anonymized using a 'decrypt' anonymizer."""

    def __init__(self):
        self.logger = logging.getLogger("presidio-anonymizer")

    def decrypt_text(self, key: str, text: str) -> str:
        """
        Decrypts a previously AES-CBC encrypted anonymized text.

        :param key: AES encryption key.
        :param text: The text for decryption.
        :returns: The decrypted text.
        """
        validate_parameter(key, "key", str)
        validate_parameter(text, "text", str)
        encoded_key = key.encode("utf8")
        if not AESCipher.is_valid_key_size(encoded_key):
            message = "Invalid input, key must be of length 128, 192 or 256 bits"
            self.logger.info(message)
            raise InvalidParamException(message)

        decrypted_text = AESCipher.decrypt(key=encoded_key, text=text)
        return decrypted_text

    def decrypt(self, text: str, entities: List[EncryptResult]) -> EngineResult:
        operators_metadata = {}
        for entity in entities:
            operators_metadata[entity.entity_type] = DecryptConfig(entity.key)
        return TextEngine().operate(text,
                                    entities,
                                    operators_metadata)
