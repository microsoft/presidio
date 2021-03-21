import logging

from presidio_anonymizer.entities.engine import TextMetadata
from presidio_anonymizer.services.validators import validate_parameter_exists


class EncryptResult(TextMetadata):
    """Information about the encrypted entity."""

    def __init__(self, key: str, start: int,
                 end: int, entity_type: str) -> 'EncryptResult':
        """
        Have the information about the entity we already encrypted and want to decrypt.

        :param key: the key used to anonymize/encrypt the text.
        :param start: start index in the anonymized text.
        :param end: end index in the anonymized text.
        """
        TextMetadata.__init__(self, start, end, entity_type)
        self.logger = logging.getLogger("presidio-anonymizer")
        validate_parameter_exists(key, "decrypt entity", "key")
        self.key = key

    def __gt__(self, other) -> bool:
        """Check result is greater by the text index start location."""
        return self.start > other.start

    @classmethod
    def from_json(cls, json: dict) -> 'EncryptResult':
        """
        Create EncryptEntity from user json.

        :param json e.g.:
        {
            "start": 0,
            "end": len(text),
            "key": "1111111111111111",
            "entity_type":"PERSON",
        }
        :return: DecryptEntity object
        """
        key = json.get("key")
        start = json.get("start")
        end = json.get("end")
        entity_type = json.get("entity_type")
        return cls(key, start, end, entity_type)
