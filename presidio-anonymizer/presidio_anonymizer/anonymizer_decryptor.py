import logging

from presidio_anonymizer.entities import InvalidParamException, \
    AnonymizedTextBuilder
from presidio_anonymizer.entities.decrypt.request import DecryptRequest
from presidio_anonymizer.entities.decrypt.response import \
    DecryptedEntity, DecryptResult
from presidio_anonymizer.services.aes_cipher import AESCipher
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

    def decrypt(self, decrypt_request: DecryptRequest) -> DecryptResult:
        text_builder = AnonymizedTextBuilder(original_text=decrypt_request.text)
        decryption_result = DecryptResult()
        for decrypted_item in decrypt_request.sorted_items(True):
            self.logger.debug(f"decrypting text in position %d-%d",
                              decrypted_item.start, decrypted_item.end)
            encrypted_text = text_builder.get_text_in_position(
                decrypted_item.start,
                decrypted_item.end)
            decrypted_text = self.decrypt_text(decrypted_item.key,
                                               encrypted_text)
            index_from_end = text_builder.replace_text_get_insertion_index(
                decrypted_text,
                decrypted_item.start,
                decrypted_item.end)
            # The following creates an intermediate list of anonymized entities,
            # ordered from end to start, and the indexes will be normalized
            # from start to end once the loop ends and the text length is deterministic.
            result_item = DecryptedEntity(
                entity_type=decrypted_item.entity_type,
                start=0,
                end=index_from_end,
                decrypted_text=decrypted_text,
            )
            decryption_result.add_item(result_item)

        decryption_result.set_text(text_builder.output_text)
        decryption_result.normalize_item_indexes()
        return decryption_result
