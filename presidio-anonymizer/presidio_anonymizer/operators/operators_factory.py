import logging
from typing import Dict, Type

from presidio_anonymizer.entities import InvalidParamError
from presidio_anonymizer.operators import (
    Custom,
    DeanonymizeKeep,
    Decrypt,
    Encrypt,
    Hash,
    Keep,
    Mask,
    Operator,
    OperatorType,
    Redact,
    Replace,
)

logger = logging.getLogger("presidio-anonymizer")

# Predefined operators
ANONYMIZERS = [Custom, Encrypt, Hash, Keep, Mask, Redact, Replace]
DEANONYMIZERS = [Decrypt, DeanonymizeKeep]


class OperatorsFactory:
    """Operators factory to get the correct operator class."""

    def __init__(
        self,
    ):
        self._anonymizers = self.__load_predefined(OperatorType.Anonymize)
        self._deanonymizers = self.__load_predefined(OperatorType.Deanonymize)

    @staticmethod
    def __load_predefined(operator_type: OperatorType) -> Dict[str, Type[Operator]]:
        """
        Return all predefined operators.

        Return a dict with {name: operator class} for each operator.
        """

        operators = (
            ANONYMIZERS if operator_type == OperatorType.Anonymize else DEANONYMIZERS
        )
        operators_dict = {
            operator().operator_name(): operator for operator in operators
        }

        return operators_dict

    @staticmethod
    def __load_predefined_deanonymizers() -> Dict[str, Type[Operator]]:
        """
        Return all predefined deanonymizers.

        Return a dict with name, deanonymizer class per each deanonymizer.
        """

        deanonymizers = [Decrypt, DeanonymizeKeep]

        deanonymizers_dict = {
            deanonymizer().operator_name(): deanonymizer
            for deanonymizer in deanonymizers
        }

        return deanonymizers_dict

    def add_anonymize_operator(self, operator: Type[Operator]):
        """Add a new anonymizer to the factory.

        :param operator: The operator class to add.
        """
        self._anonymizers[operator().operator_name()] = operator

    def add_deanonymize_operator(self, operator: Type[Operator]):
        """Add a new deanonymizer to the factory.

        :param operator: The operator class to add.
        """
        self._deanonymizers[operator().operator_name()] = operator

    def remove_anonymize_operator(self, operator: Type[Operator]):
        """Remove an anonymizer from the factory.

        :param operator: The operator class to remove.
        """
        if operator().operator_name() not in self._anonymizers:
            logger.error(
                f"Operator {operator().operator_name()} not found in anonymizers list"
            )
            raise InvalidParamError(
                f"Operator {operator().operator_name()} not found in anonymizers list"
            )
        self._anonymizers.pop(operator().operator_name(), None)

    def remove_deanonymize_operator(self, operator: Type[Operator]):
        """Remove a deanonymizer from the factory.

        :param operator: The operator class to remove.
        """
        if operator().operator_name() not in self._deanonymizers:
            logger.error(
                f"Operator {operator().operator_name()} not found in deanonymizers list"
            )
            raise InvalidParamError(
                f"Operator {operator().operator_name()} not found in deanonymizers list"
            )
        self._deanonymizers.pop(operator().operator_name(), None)

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
            logger.error(f"No such operator type {operator_type}")
            raise InvalidParamError(f"Invalid operator type '{operator_type}'.")

        operator = operators_by_type.get(operator_name)
        if not operator:
            logger.error(f"No such operator {operator_name}")
            raise InvalidParamError(f"Invalid operator class '{operator_name}'.")

        return operator()

    def __get_operators_classes(self) -> Dict[OperatorType, Dict[str, Type[Operator]]]:
        operator_classes = {
            OperatorType.Anonymize: self.get_anonymizers(),
            OperatorType.Deanonymize: self.get_deanonymizers(),
        }
        return operator_classes

    def get_anonymizers(self) -> Dict[str, Type[Operator]]:
        """Return all anonymizers classes currently available."""
        return self._anonymizers

    def get_deanonymizers(self) -> Dict[str, Type[Operator]]:
        """Return all deanonymizers classes currently available."""
        return self._deanonymizers

    def __get_operators_by_type(
        self, operator_type: OperatorType
    ) -> Dict[str, Type[Operator]]:
        return self.__get_operators_classes().get(operator_type)
