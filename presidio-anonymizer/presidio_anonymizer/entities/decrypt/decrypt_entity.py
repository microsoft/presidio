import logging
from typing import Dict, List

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.manipulator.manipulated_result_item import \
    ManipulatedResultItem


class DecryptEntity:
    """Information about the decrypt entity."""

    def __init__(self, key: str, start: int,
                 end: int) -> 'DecryptEntity':
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
        return cls(key, start, end)

    @classmethod
    def multiple_from_json(cls, json: Dict) -> List['DecryptEntity']:
        """
        Create DecryptEntity list.

        :param json e.g.:
        {
            "text": text,
            "items": [{
                "start": 0,
                "end": len(text),
                "key": "1111111111111111",
            }],
        }
        :return: DecryptRequest
        """
        items = []
        decrypt_entity = json.get("items")
        if decrypt_entity:
            for result in decrypt_entity:
                items.append(DecryptEntity.from_json(result))
        return items

    @classmethod
    def from_anonymizer_entity(cls, key: str,
                               entity: ManipulatedResultItem) -> 'DecryptEntity':
        """
        Create DecryptEntity from AnonymizerEntity.

        :param key: key yo decrypt the text with (the one which encrypted the text).
        :param entity: AnonymizedEntity returned from the anonymizer /anonymize method.
        :return: DecryptEntity.
        """
        return cls(key, entity.start, entity.end)
