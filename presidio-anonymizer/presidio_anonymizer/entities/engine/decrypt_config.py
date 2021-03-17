from presidio_anonymizer.entities.engine.operator_metadata import OperatorMetadata
from presidio_anonymizer.operators import OperatorType
from presidio_anonymizer.operators.decrypt import Decrypt


class DecryptConfig(OperatorMetadata):
    def __init__(self, key: str = None):
        """
        Create AnonymizerConfig entity.

        :param anonymizer_name: the anonymizer name string - represents the class
        of the anonymizer in lower case letters. e.g.: redact
        :param params: the parameters to use in the selected anonymizer class
        """

        params = {Decrypt.KEY: key}
        OperatorMetadata.__init__(self, OperatorType.Decrypt, params, Decrypt.NAME)
