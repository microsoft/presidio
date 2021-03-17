"""Handle the anonymizers data - anonymizer class and params."""
import logging
from typing import Dict


class AnonymizerConfig:
    """Handle the anonymizers data - anonymizer class and params."""
    logger = logging.getLogger("presidio-anonymizer")

    def __init__(self, anonymizer_name: str, params: Dict = None):
        """
        Create AnonymizerConfig entity.

        :param anonymizer_name: the anonymizer name string - represents the class
        of the anonymizer in lower case letters. e.g.: redact
        :param params: the parameters to use in the selected anonymizer class
        """
        self.anonymizer_name = anonymizer_name
        self.params = params
        if not params:
            self.params = {}

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

        anonymizer_class_equals = self.anonymizer_name == other.anonymizer_name
        return self.params == other.params and anonymizer_class_equals


