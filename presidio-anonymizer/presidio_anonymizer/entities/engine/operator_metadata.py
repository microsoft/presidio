from abc import ABC
from typing import Dict

from presidio_anonymizer.operators import OperatorType


class OperatorMetadata(ABC):

    def __init__(
            self,
            operator_type: OperatorType,
            params: Dict,
            operator_name: str
    ):
        self.operator_type = operator_type
        self.operator_name = operator_name
        self.params = params
