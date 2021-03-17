import logging
from abc import ABC
from typing import Dict

from presidio_anonymizer.operators import OperatorType
from presidio_anonymizer.operators.decrypt import Decrypt


class OperatorMetadata(ABC):

    def __init__(
            self,
            operator_type: OperatorType,
            params: Dict,
            operator_name: str
    ):
        self.logger = logging.getLogger("presidio-anonymizer")
        self.operator_type = operator_type
        self.operator_name = operator_name
        self.params = params



    @classmethod
    def from_decrypt_entity(cls, key: str):
        return cls(OperatorType.Decrypt, {Decrypt.KEY: key}, Decrypt.NAME)
