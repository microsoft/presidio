import logging

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.engine import OperatorMetadata
from presidio_anonymizer.operators import Decrypt
from presidio_anonymizer.operators import OperatorType


class DecryptConfig(OperatorMetadata):
    """Decrypt configuration for each text entity of the decryption."""

    def __init__(self, key: str):
        """
        Create AnonymizerConfig entity.

        :param anonymizer_name: the anonymizer name string - represents the class
        of the anonymizer in lower case letters. e.g.: redact
        :param params: the parameters to use in the selected anonymizer class
        """
        self.logger = logging.getLogger("presidio-anonymizer")
        params = {Decrypt.KEY: key}
        if not key:
            self.__validate_field("key")
        OperatorMetadata.__init__(self, OperatorType.Decrypt, params, Decrypt.NAME)

    def __validate_field(self, field_name: str):
        self.logger.debug(f"invalid parameter, {field_name} cannot be empty")
        raise InvalidParamException(
            f"Invalid input, config must contain {field_name}"
        )
