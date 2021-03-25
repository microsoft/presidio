import logging
from typing import Dict

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.services.validators import validate_parameter_exists


class OperatorConfig:
    """Abstract class to hold the data of the required operator."""

    logger = logging.getLogger("presidio-anonymizer")

    def __init__(
            self,
            operator_name: str,
            params: Dict = None
    ):
        self.logger = logging.getLogger("presidio-anonymizer")
        self.operator_name = operator_name
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

    def __eq__(self, other: 'OperatorConfig'):
        """Verify two OperatorConfigs are equal."""
        operator_name = self.operator_name == other.operator_name
        return (self.params == other.params
                and operator_name)

    def __validate_fields(self):
        validate_parameter_exists(self.operator_name, "operator config", "operator_name")

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
