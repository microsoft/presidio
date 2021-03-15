import logging
from typing import List

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.decrypt.decrypt_entity import DecryptEntity
from presidio_anonymizer.entities.decrypt.decrypt_result import DecryptResult
from presidio_anonymizer.entities.decrypt.decrypted_entity import DecryptedEntity
from presidio_anonymizer.entities.manipulator.text_manipulation_data import \
    TextManipulationData
from presidio_anonymizer.services.aes_cipher import AESCipher
from presidio_anonymizer.services.text_builder import TextBuilder
from presidio_anonymizer.services.text_manipulator import TextManipulator
from presidio_anonymizer.services.validators import validate_parameter


class AnonymizerDecryptor:
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

    def decrypt(self, text: str, entities: List[DecryptEntity]) -> DecryptResult:
        manipultaion_enetities = []
        for entity in entities:
            manipulation_data = TextManipulationData.create_from_decrypt_entity(entity)
            manipultaion_enetities.append(manipulation_data)
        result = TextManipulator().manipulate_text(text, manipultaion_enetities)
        result.items
