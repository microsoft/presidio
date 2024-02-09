from typing import Type, Dict

from presidio_anonymizer.operators import OperatorType, Operator


def create_reverser_operator(operator_type:OperatorType) -> Type[Operator]:
    class ReverserOperator(Operator):
        def operate(self, text: str, params: Dict = None) -> str:
            return text[::-1]

        def validate(self, params: Dict = None) -> None:
            pass

        def operator_name(self) -> str:
            return "Reverser"

        def operator_type(self) -> OperatorType:
            return operator_type

    return ReverserOperator
