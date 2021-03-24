import logging
from typing import Dict

from presidio_anonymizer.entities.engine import TextMetadata
from presidio_anonymizer.entities.engine.result import AnonymizedEntity


class AnonymizerResult(TextMetadata):
    """Information about the encrypted entity."""

    def __init__(self, start: int,
                 end: int, entity_type: str) -> 'AnonymizerResult':
        """
        Have the information about the entity we already encrypted and want to decrypt.

        :param key: the key used to anonymize/encrypt the text.
        :param start: start index in the anonymized text.
        :param end: end index in the anonymized text.
        """
        TextMetadata.__init__(self, start, end, entity_type)
        self.logger = logging.getLogger("presidio-anonymizer")

    def __gt__(self, other) -> bool:
        """Check result is greater by the text index start location."""
        return self.start > other.start

    @classmethod
    def from_json(cls, json: Dict) -> 'AnonymizerResult':
        """
        Create EncryptEntity from user json.

        :param json e.g.:
        {
            "start": 0,
            "end": 10,
            "key": "1111111111111111",
            "entity_type":"PERSON",
        }
        :return: DecryptEntity object
        """
        key = json.get("key")
        start = json.get("start")
        end = json.get("end")
        entity_type = json.get("entity_type")
        return cls(start, end, entity_type)

    @classmethod
    def from_anonymized_entity(cls, anonymized_entity: AnonymizedEntity):
        """
        Convert anonymized entity returned from anonymizer engine to encrypt result.

        :param key: the key we used to encrypt the text.
        :param anonymized_entity: a single anonymizer encrypt result we received
        from the engine.
        :return:
        """
        return cls(anonymized_entity.start, anonymized_entity.end,
                   anonymized_entity.entity_type)
