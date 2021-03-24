"""Decrypt encrypted text by the 'encrypt' anonymizer."""
import logging
from typing import List

from presidio_anonymizer.core.engine_base import EngineBase
from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.engine.anonymizer_result import AnonymizerResult
from presidio_anonymizer.entities.engine.deanonymize_config import DeanonymizeConfig
from presidio_anonymizer.entities.engine.result.engine_result import EngineResult
from presidio_anonymizer.operators.aes_cipher import AESCipher
from presidio_anonymizer.services.validators import validate_parameter


class DecryptEngine(EngineBase):
    """Decrypting text that was previously anonymized using a 'decrypt' anonymizer."""

    def __init__(self):
        self.logger = logging.getLogger("presidio-anonymizer")
        EngineBase.__init__(self)

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

    def deanonymize(self, text: str, entities: List[AnonymizerResult]) -> EngineResult:
        """
        Receive the text and the entities and decrypt accordingly.

        :param text: the full text with the encrypted entities
        :param entities: list of encrypted entities
        :return: EngineResult - the new text and data about the decrypted entities.
        """
        operators_metadata = {}
        for entity in entities:
            operators_metadata[entity.entity_type] = DeanonymizeConfig(entity.key)
        return self._operate(text,
                             entities,
                             operators_metadata)

