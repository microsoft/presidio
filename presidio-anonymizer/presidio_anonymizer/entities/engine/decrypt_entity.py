import logging
from typing import Dict, List

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.engine.text_metadata import TextMetadata


class DecryptEntity(TextMetadata):
    """Information about the decrypt entity."""
    def __init__(self, key: str, start: int,
                 end: int, entity_type: str) -> 'DecryptEntity':
        """
        Create DecryptEntity.

        :param key: the key used to anonymize/encrypt the text.
        :param start: start index in the anonymized text.
        :param end: end index in the anonymized text.
        """
        self.logger = logging.getLogger("presidio-anonymizer")
        self.start = start
        self.end = end
        self.key = key
        self.entity_type = entity_type
        self.__validate_fields()

    def __gt__(self, other) -> bool:
        return self.start > other.start

    def __validate_fields(self):
        if self.key is None:
            self.__validate_field("key")
        if self.start is None:
            self.__validate_field("start")
        if self.end is None:
            self.__validate_field("end")
        if self.entity_type is None:
            self.__validate_field("entity_type")
        if self.start < 0 or self.end < 0:
            raise InvalidParamException(
                f"Invalid input, decrypt entity start and end must be positive"
            )
        if self.start >= self.end:
            raise InvalidParamException(
                f"Invalid input, decrypt entity start index '{self.start}' "
                f"must be smaller than end index '{self.end}'"
            )

    def __validate_field(self, field_name: str):
        self.logger.debug(f"invalid parameter, {field_name} cannot be empty")
        raise InvalidParamException(
            f"Invalid input, decrypt entity must contain {field_name}"
        )

    def get_start(self):
        return self.entity_type

    def get_end(self):
        return self.entity_type

    def get_entity_type(self):
        return self.entity_type

    @classmethod
    def from_json(cls, json: dict) -> 'DecryptEntity':
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




