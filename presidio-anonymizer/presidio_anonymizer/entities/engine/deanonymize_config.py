import logging
from typing import Dict

from presidio_anonymizer.entities.engine import OperatorConfig
from presidio_anonymizer.operators import OperatorType


class DeanonymizeConfig(OperatorConfig):
    """Decrypt configuration for each text entity of the decryption."""

    def __init__(self, operator_name: str, params: Dict = None):
        """
        Create AnonymizerConfig entity.

        :param anonymizer_name: the anonymizer name string - represents the class
        of the anonymizer in lower case letters. e.g.: redact
        :param params: the parameters to use in the selected anonymizer class
        """
        self.logger = logging.getLogger("presidio-anonymizer")
        OperatorConfig.__init__(self, operator_type=OperatorType.Deanonymize, params=params,
                                operator_name=operator_name)
