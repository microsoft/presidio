from typing import Dict

from presidio_anonymizer.entities import RecognizerResult, AnonymizerConfig
from presidio_anonymizer.entities.decrypt.decrypt_entity import DecryptEntity
from presidio_anonymizer.operators import Operator, Encrypt
from presidio_anonymizer.operators.decrypt import Decrypt


class TextManipulationItem:
    def __init__(
            self,
            start: int,
            end: int,
            entity_type: str,
            score: float,
            params: Dict,
            manipulator_class: Operator
    ):
        """Create DecryptedEntity.

        :param start: start index in the decrypted text.
        :param end: end index in the decrypted text.
        """
        self.start = start
        self.end = end
        self.score = score
        self.entity_type = entity_type
        self.manipulator_class = manipulator_class
        self.params = params

    def __gt__(self, other):
        return self.end > other.end

    @classmethod
    def from_anonymizer_data(cls, result: RecognizerResult,
                             anonymizer: AnonymizerConfig):
        return cls(result.start, result.end, result.entity_type, result.score,
                   anonymizer.params, anonymizer.anonymizer_class)

    @classmethod
    def from_decrypt_entity(cls, entity: DecryptEntity):
        return cls(entity.start, entity.end, "", 0, {Encrypt.KEY: entity.key}, Decrypt)
