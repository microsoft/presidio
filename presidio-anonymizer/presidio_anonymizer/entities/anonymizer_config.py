"""Handle the anonymizers data - anonymizer class and params."""
import logging
from typing import Dict

from presidio_anonymizer.anonymizers import Anonymizer
from presidio_anonymizer.entities import InvalidParamException


class AnonymizerConfig:
    """Handle the anonymizers data - anonymizer class and params."""

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

    def __init__(self, anonymizer_name: str, params: Dict = None):
        """
        Create AnonymizerConfig entity.

        :param anonymizer_name: the anonymizer name string - represents the class
        of the anonymizer in lower case letters. e.g.: redact
        :param params: the parameters to use in the selected anonymizer class
        """
        self.logger = logging.getLogger("presidio-anonymizer")
        self.anonymizer_class = self.__get_anonymizer_class(anonymizer_name)
        self.params = params
        if not params:
            self.params = {}

    def __get_anonymizer_class(self, anonymizer_name: str) -> Anonymizer:
        """
        Extract the anonymizer class from the anonymizers list.

        :param anonymizer_name: a single anonymizer value
        :return: Anonymizer
        """
        anonymizer_class = Anonymizer.get_anonymizers().get(anonymizer_name)
        if not anonymizer_class:
            self.logger.error(f"No such anonymizer class {anonymizer_name}")
            raise InvalidParamException(
                f"Invalid anonymizer class '{anonymizer_name}'."
            )
        self.logger.debug(f"applying class {anonymizer_class}")
        return anonymizer_class

    def __eq__(self, other):
        """Verify two AnonymizerConfig are equal."""

        anonymizer_class_equals = self.anonymizer_class == other.anonymizer_class
        return self.params == other.params and anonymizer_class_equals
