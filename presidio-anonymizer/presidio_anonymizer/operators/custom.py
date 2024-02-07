"""Replaces the PII text with function result."""
from typing import Dict
from inspect import signature

from presidio_anonymizer.operators import Operator, OperatorType
from presidio_anonymizer.entities import InvalidParamException


class Custom(Operator):
    """
    Replace PII text entity with the results of a function executed on the PII text.

    The function retrun type must be a string
    """

    LAMBDA = "lambda"

    def operate(self, text: str = None, params: Dict = None) -> str:
        """:return: result of function executed on the text."""
        return self._call_lambda(text, params)

    def validate(self, params: Dict) -> None:
        """Validate the provided function is returning a string."""
        if callable(params.get(self.LAMBDA)):
            if not type(self._call_lambda("PII", params)) == str:
                raise InvalidParamException("Function return type must be a str")

        else:
            raise InvalidParamException("New value must be a callable function")

    def operator_name(self) -> str:
        """Return operator name."""
        return "custom"

    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Anonymize

    def _call_lambda(self, text: str = None, params: Dict = None):
        new_val = params.get(self.LAMBDA)
        sig = signature(new_val)
        if len(sig.parameters) == 1:
            return new_val(text)
        return new_val(text, params.get("entity_type"))
