"""Hashes the PII text entity."""
from hashlib import sha256, sha512, md5
from typing import Dict

from presidio_anonymizer.operators import Operator, OperatorType
from presidio_anonymizer.services.validators import validate_parameter_in_range


class Keep(Operator):
    """
    This is a no-op anonymizer that keeps the PII text unmodified
    
    This is useful when you don't want to anonymize some types of PII, 
    but wants to keep track of it with the other PIIs
    """

    def operate(self, text: str = None, params: Dict = None) -> str:
        """
        :return: original text
        """
        return text

    def validate(self, params: Dict = None) -> None:
        pass

    def operator_name(self) -> str:
        """Return operator name."""
        return "keep"

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Anonymize
