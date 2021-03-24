import logging
from abc import ABC
from typing import Dict

from presidio_anonymizer.operators import OperatorType, operator

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.services.validators import validate_parameter_exists


class OperatorConfig(ABC):
    """Abstract class to hold the data of the required operator."""

    logger = logging.getLogger("presidio-anonymizer")

    def __init__(
            self,
            operator_type: OperatorType,
            operator_name: str,
            params: Dict
    ):
        self.logger = logging.getLogger("presidio-anonymizer")
        self.operator_name = operator_name
        self.operator_type = operator_type
        if not params:
            params = {}
        self.params = params
        self.__validate_fields()

    @classmethod
    def from_json(cls, params: Dict):
        """
        Create AnonymizerConfig from json.

        :param params: json e.g.: {
            "type": "mask",
            "masking_char": "*",
            "chars_to_mask": 4,
            "from_end": true
        }
        :return: AnonymizerConfig
        """
        operator_name = params.get("type")
        if operator_name:
            params.pop("type")
        return cls(operator_name, params)

    def __eq__(self, other):
        """Verify two OperatorConfigs are equal."""
        anonymizer_class_equals = self.operator_name == other.operator_name
        operator_types_equal = self.operator_type == other.operator_type
        return (self.params == other.params
                and anonymizer_class_equals
                and operator_types_equal)

    def __validate_fields(self):
        validate_parameter_exists(self.operator_name, "config", "operator_name")
        validate_parameter_exists(self.operator_type, "config", "operator_type")
        if self.operator_type not in operator.types:
            raise InvalidParamException(
                f"Invalid input, invalid operator type {self.operator_type}"
            )

    def __field_validation_error(self, field_name: str):
        self.logger.debug(f"invalid parameter, {field_name} cannot be empty")
        raise InvalidParamException(
            f"Invalid input, config must contain {field_name}"
        )

    @classmethod
    def from_json(cls, params: Dict):
        """
        Create AnonymizerConfig from json.

        :param params: json e.g.: {
            "type": "mask",
            "masking_char": "*",
            "chars_to_mask": 4,
            "from_end": true
        }
        :return: AnonymizerConfig
        """
        operator_name = params.get("type")
        if operator_name:
            params.pop("type")
        return cls(operator_name, params)