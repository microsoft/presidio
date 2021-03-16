import logging
from typing import List

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.decrypt.decrypt_entity import DecryptEntity
from presidio_anonymizer.entities.engine.decrypt_result_item import DecryptResultItem
from presidio_anonymizer.entities.engine.engine_result import EngineResult
from presidio_anonymizer.entities.manipulator.text_manipulation_data import \
    TextManipulationData
from presidio_anonymizer.services.aes_cipher import AESCipher
from presidio_anonymizer.services.text_manipulator import TextManipulator
from presidio_anonymizer.services.validators import validate_parameter


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

    def decrypt(self, text: str, entities: List[DecryptEntity]) -> EngineResult:
        manipulation_entities = []
        for entity in entities:
            manipulation_data = TextManipulationData.from_decrypt_entity(entity)
            manipulation_entities.append(manipulation_data)
        manipulator_result = TextManipulator().manipulate_text(text,
                                                               manipulation_entities)
        decryption_result = EngineResult(manipulator_result.text, [])
        for item in manipulator_result.items:
            decrypted_entity = DecryptResultItem.from_manipulated_entity(item)
            decryption_result.append_item(decrypted_entity)
        return decryption_result
