import logging
from typing import Dict

from presidio_anonymizer.entities import AnonymizerConfig
from presidio_anonymizer.operators import Encrypt, OperatorType
from presidio_anonymizer.operators.decrypt import Decrypt


class OperatorMetadata:
    def __init__(
            self,
            operator_type: OperatorType,
            params: Dict,
            operator_name: str
    ):
        """Create DecryptedEntity.

        :param start: start index in the decrypted text.
        :param end: end index in the decrypted text.
        """
        self.logger = logging.getLogger("presidio-anonymizer")
        self.operator_type = operator_type
        self.operator_name = operator_name
        self.params = params

    def __gt__(self, other):
        return self.end > other.end

    @classmethod
    def from_anonymizer_data(cls, anonymizer: AnonymizerConfig):
        return cls(OperatorType.Anonymize, anonymizer.params,
                   anonymizer.anonymizer_name)

    @classmethod
    def from_decrypt_entity(cls, key: str):
        return cls(OperatorType.Decrypt, {Decrypt.KEY: key}, Decrypt.NAME)
