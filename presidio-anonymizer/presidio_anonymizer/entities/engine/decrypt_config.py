import logging

from presidio_anonymizer.entities.engine import OperatorConfig
from presidio_anonymizer.operators import Decrypt
from presidio_anonymizer.operators import OperatorType
from presidio_anonymizer.services.validators import validate_parameter_exists


class DecryptConfig(OperatorConfig):
    """Decrypt configuration for each text entity of the decryption."""

    def __init__(self, key: str):
        """
        Create AnonymizerConfig entity.

        :param anonymizer_name: the anonymizer name string - represents the class
        of the anonymizer in lower case letters. e.g.: redact
        :param params: the parameters to use in the selected anonymizer class
        """
        self.logger = logging.getLogger("presidio-anonymizer")
        validate_parameter_exists(key, "config", "key")
        params = {Decrypt.KEY: key}
        OperatorConfig.__init__(self, OperatorType.Decrypt, params, Decrypt.NAME)
