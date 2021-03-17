"""Handle the anonymizers data - anonymizer class and params."""
import logging
from typing import Dict

from presidio_anonymizer.entities.engine import OperatorMetadata
from presidio_anonymizer.operators import OperatorType


class AnonymizeConfig(OperatorMetadata):
    """Handle the anonymizers data - anonymizer class and params."""

    logger = logging.getLogger("presidio-anonymizer")

    def __init__(self, anonymizer_name: str, params: Dict = None):
        """
        Create AnonymizerConfig entity.

        :param anonymizer_name: the anonymizer name string - represents the class
        of the anonymizer in lower case letters. e.g.: redact
        :param params: the parameters to use in the selected anonymizer class
        """
        if not params:
            params = {}
        OperatorMetadata.__init__(self, OperatorType.Anonymize, params, anonymizer_name)

    @classmethod
    def from_json(cls, params: dict):
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
        anonymizer_name = params.get("type")
        if anonymizer_name:
            params.pop("type")
        return cls(anonymizer_name, params)

    def __eq__(self, other):
        """Verify two AnonymizerConfig are equal."""
        anonymizer_class_equals = self.operator_name == other.operator_name
        operator_types_equal = self.operator_type == other.operator_type
        return (self.params == other.params
                and anonymizer_class_equals
                and operator_types_equal)
