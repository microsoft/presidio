import logging

from presidio_anonymizer.entities import InvalidParamException, AnonymizedEntity


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
    def from_anonymizer_entity(cls, key: str,
                               entity: AnonymizedEntity) -> 'DecryptEntity':
        """
        Create DecryptEntity from AnonymizerEntity.

        :param key: key yo decrypt the text with (the one which encrypted the text).
        :param entity: AnonymizedEntity returned from the anonymizer /anonymize method.
        :return: DecryptEntity.
        """
        return cls(key, entity.start, entity.end)
