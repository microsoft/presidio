import logging

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.engine import TextMetadata


class EncryptResult(TextMetadata):
    """Information about the decrypt entity."""

    def __init__(self, key: str, start: int,
                 end: int, entity_type: str) -> 'EncryptResult':
        """
        Create DecryptEntity.

        :param key: the key used to anonymize/encrypt the text.
        :param start: start index in the anonymized text.
        :param end: end index in the anonymized text.
        """
        TextMetadata.__init__(self, start, end, entity_type)
        self.logger = logging.getLogger("presidio-anonymizer")
        self.key = key
        self.__validate_fields()

    def __gt__(self, other) -> bool:
        """Check result is greater by the text index start location."""
        return self.start > other.start

    def __validate_fields(self):
        if self.key is None:
            self.__validate_field("key")

    def __validate_field(self, field_name: str):
        self.logger.debug(f"invalid parameter, {field_name} cannot be empty")
        raise InvalidParamException(
            f"Invalid input, decrypt entity must contain {field_name}"
        )

    @classmethod
    def from_json(cls, json: dict) -> 'EncryptResult':
        """
        Create DecryptEntity from user json.

        :param json e.g.:
        {
            "start": 0,
            "end": len(text),
            "key": "1111111111111111",
        }
        :return: DecryptEntity object
        """
        key = json.get("key")
        start = json.get("start")
        end = json.get("end")
        entity_type = json.get("entity_type")
        return cls(key, start, end, entity_type)
