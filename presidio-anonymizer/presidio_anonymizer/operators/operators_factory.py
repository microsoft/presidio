import logging
from typing import Dict

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.operators import OperatorType, Operator


class OperatorsFactory:
    """Operators factory to get the correct operator class."""

    _anonymizers: Dict = None
    _decryptors: Dict = None

    def __init__(self):
        self.logger = logging.getLogger("presidio-anonymizer")

    def create_operator_class(self, operator_name: str,
                              operator_type: OperatorType) -> Operator:
        """
        Extract the operator class from the operators list.

        :param operator_type: Either Anonymize or Decrypt to defer between operators.
        :type operator_name: operator name.
        :return: operator class entity.
        """
        operator_class = None
        if operator_type == OperatorType.Anonymize:
            operator_class = OperatorsFactory.get_anonymizers().get(operator_name)
        if operator_type == OperatorType.Decrypt:
            operator_class = OperatorsFactory.get_decryptors().get(operator_name)
        if not operator_class:
            self.logger.error(f"No such operator class {operator_name}")
            raise InvalidParamException(
                f"Invalid operator class '{operator_name}'."
            )
        self.logger.debug(f"applying class {operator_class}")
        return operator_class()

    @staticmethod
    def get_anonymizers() -> \
            Dict[str, "Operator"]:
        """Return all anonymizers classes currently available."""
        if not OperatorsFactory._anonymizers:
            OperatorsFactory._anonymizers = OperatorsFactory.__get_operators_by_type(
                OperatorType.Anonymize)
        return OperatorsFactory._anonymizers

    @staticmethod
    def get_decryptors() -> \
            Dict[str, "Operator"]:
        """Return all decryptors classes currently available."""
        if not OperatorsFactory._decryptors:
            OperatorsFactory._decryptors = OperatorsFactory.__get_operators_by_type(
                OperatorType.Decrypt)
        return OperatorsFactory._decryptors

    @staticmethod
    def __get_operators_by_type(manipulator_type: OperatorType):
        manipulators = Operator.__subclasses__()
        manipulators = list(filter(
            lambda cls: cls.operator_type(cls) == manipulator_type,
            manipulators))
        return {
            cls.operator_name(cls): cls for
            cls in manipulators
        }
