import logging
from typing import Dict

from presidio_anonymizer.entities.engine import PIIEntity
from presidio_anonymizer.entities.engine.result import OperatorResult


class AnonymizerResult(PIIEntity):
    """Information about the encrypted entity."""

    def __init__(self, start: int, end: int, entity_type: str) -> "AnonymizerResult":
        """
        Information about the anonymized entity we want to deanonymize.

        :param start: start index in the anonymized text.
        :param end: end index in the anonymized text.
        :param entity_type: the type of the PII.
        """
        PIIEntity.__init__(self, start, end, entity_type)
        self.logger = logging.getLogger("presidio-anonymizer")

    @classmethod
    def from_json(cls, json: Dict) -> "AnonymizerResult":
        """
        Create AnonymizerResult from user json.

        :param json: json representation for this anonymizer result. For example:
        {
            "start": 0,
            "end": 10,
            "key": "1111111111111111",
            "entity_type":"PERSON",
        }
        """
        start = json.get("start")
        end = json.get("end")
        entity_type = json.get("entity_type")
        return cls(start, end, entity_type)

    @classmethod
    def from_operator_result(cls, operator_result: OperatorResult):
        """
        Convert anonymized entity returned from anonymizer engine to encrypt result.

        :param operator_result: a single anonymizer encrypt result we received
        from the engine.
        :return:
        """
        return cls(
            operator_result.start, operator_result.end, operator_result.entity_type
        )
