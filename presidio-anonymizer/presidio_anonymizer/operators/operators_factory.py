import logging
from typing import Dict

from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.operators import OperatorType, Operator


class OperatorsFactory:
    """Operators factory to get the correct operator class."""

    _anonymizers: Dict = None
    _deanonymizers: Dict = None
    _operator_class: Dict = None

    def __init__(self):
        self.logger = logging.getLogger("presidio-anonymizer")

    def create_operator_class(
        self, operator_name: str, operator_type: OperatorType
    ) -> Operator:
        """
        Extract the operator class from the operators list.

        :param operator_type: Either Anonymize or Decrypt to defer between operators.
        :type operator_name: operator name.
        :return: operator class entity.
        """
        operators_by_type = self.__get_operators_classes().get(operator_type)
        if not operators_by_type:
            self.logger.error(f"No such operator type {operator_type}")
            raise InvalidParamException(f"Invalid operator type '{operator_type}'.")
        operator_class = operators_by_type.get(operator_name)
        if not operator_class:
            self.logger.error(f"No such operator class {operator_name}")
            raise InvalidParamException(f"Invalid operator class '{operator_name}'.")
        self.logger.debug(f"applying class {operator_class}")
        return operator_class()

    @staticmethod
    def __get_operators_classes():
        if not OperatorsFactory._operator_class:
            OperatorsFactory._operator_class = {
                OperatorType.Anonymize: OperatorsFactory.get_anonymizers(),
                OperatorType.Deanonymize: OperatorsFactory.get_deanonymizers(),
            }
        return OperatorsFactory._operator_class

    @staticmethod
    def get_anonymizers() -> Dict[str, "Operator"]:
        """Return all anonymizers classes currently available."""
        if not OperatorsFactory._anonymizers:
            OperatorsFactory._anonymizers = OperatorsFactory.__get_operators_by_type(
                OperatorType.Anonymize
            )
        return OperatorsFactory._anonymizers

    @staticmethod
    def get_deanonymizers() -> Dict[str, "Operator"]:
        """Return all deanonymizers classes currently available."""
        if not OperatorsFactory._deanonymizers:
            OperatorsFactory._deanonymizers = OperatorsFactory.__get_operators_by_type(
                OperatorType.Deanonymize
            )
        return OperatorsFactory._deanonymizers

    @staticmethod
    def __get_operators_by_type(operator_type: OperatorType):
        operators = Operator.__subclasses__()
        return {
            cls.operator_name(cls): cls
            for cls in operators
            if cls.operator_type(cls) == operator_type
        }
