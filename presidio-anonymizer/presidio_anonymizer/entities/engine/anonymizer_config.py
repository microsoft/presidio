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

    @classmethod
    def get_anonymizer_configs_from_json(
            cls, data: Dict
    ) -> Dict[str, 'AnonymizerConfig']:
        """
        Go over the anonymizers and get the relevant anonymizer class for it.

        Inserts the class to the anonymizer so the engine will use it.
        :param data: contains the text, configuration and analyzer_results
        value - AnonynmizerConfig
        """
        anonymizers_config = {}
        anonymizers = data.get("anonymizers")
        if anonymizers is not None:
            for key, anonymizer_json in anonymizers.items():
                cls.logger.debug(
                    f"converting {anonymizer_json} to anonymizer config class"
                )
                anonymizer_config = AnonymizerConfig.from_json(anonymizer_json)
                anonymizers_config[key] = anonymizer_config
        return anonymizers_config
