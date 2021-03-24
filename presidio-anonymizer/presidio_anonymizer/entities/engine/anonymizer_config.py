"""Handle the anonymizers data - anonymizer class and params."""
import logging
from typing import Dict

from presidio_anonymizer.entities.engine import OperatorConfig
from presidio_anonymizer.operators import OperatorType


class AnonymizerConfig(OperatorConfig):
    """Handle the anonymizers (operators) data - anonymizer class name and params."""

    logger = logging.getLogger("presidio-anonymizer")

    def __init__(self, anonymizer_name: str, params: Dict = None):
        """
        Create AnonymizerConfig entity.

        :param anonymizer_name: the anonymizer name string - represents the class
        of the anonymizer in lower case letters. e.g.: redact
        :param params: the parameters to use in the selected anonymizer class
        """
        OperatorConfig.__init__(self, operator_type=OperatorType.Anonymize,
                                params=params, operator_name=anonymizer_name)

