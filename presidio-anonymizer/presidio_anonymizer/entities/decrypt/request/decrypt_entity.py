import logging

from presidio_anonymizer.entities import InvalidParamException, AnonymizedEntity


class DecryptEntity:
    """Information about the decrypt entity."""

    def __init__(self, key: str, entity_type: str, start: int,
                 end: int, anonymized_text: str):
        """Create DecryptEntity.

        :param anonymizer: name of the anonymizer.
        :param entity_type: type of the PII entity.
        :param start: start index in the anonymized text.
        :param end: end index in the anonymized text.
        :param anonymized_text: the PII anonymized text.
        """
        self.logger = logging.getLogger("presidio-anonymizer")
        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.anonymized_text = anonymized_text
        self.key = key
        self.__validate_fields()

    def __gt__(self, other):
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
    def from_json(cls, json: dict):
        key = json.get("key")
        start = json.get("start")
        end = json.get("end")
        entity_type = json.get("entity_type")
        anonymized_text = json.get("anonymized_text")
        return cls(key, entity_type, start, end, anonymized_text)

    @classmethod
    def from_anonymizer_entity(cls, key: str, entity: AnonymizedEntity):
        return cls(key, entity.entity_type, entity.start, entity.end,
                   entity.anonymized_text)
