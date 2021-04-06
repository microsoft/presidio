"""Replaces the PII text with function result."""
from typing import Dict

from presidio_anonymizer.operators import Operator, OperatorType
from presidio_anonymizer.entities import InvalidParamException


class Custom(Operator):
    """
    Replace PII text entity with the results of a function executed on the PII text.

    The function retrun type must be a string
    """

    NEW_VALUE = "new_value"

    def operate(self, text: str = None, params: Dict = None) -> str:
        """:return: result of function executed on the text."""
        new_val = params.get(self.NEW_VALUE)
        return new_val(text)

    def validate(self, params: Dict = None) -> None:
        """Validate the provided function is returning a string."""
        new_val = params.get(self.NEW_VALUE)
        if callable(new_val):
            if (type(new_val("PII")) == str):
                return
            else:
                raise InvalidParamException("Invalid function return type. must be a str")
        else:
            raise InvalidParamException("New value must be a callable function")

    def operator_name(self) -> str:
        """Return operator name."""
        return "custom"

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Anonymize
