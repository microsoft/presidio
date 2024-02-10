from typing import Type, Dict

from presidio_anonymizer.operators import OperatorType, Operator


def create_instance_counter_anonymizer() -> Type[Operator]:
    class InstanceCounterAnonymizer(Operator):
        def operate(self, text: str, params: Dict = None) -> str:
            if "entity_counters" not in params:
                raise ValueError("A dict holding entity counters is required.")

            entity_counters = params["entity_counters"]
            entity_type = params["entity_type"]
            if entity_type not in entity_counters:
                entity_counters[entity_type] = 0

            text = f"<{entity_type}_{entity_counters[entity_type]}>"
            entity_counters[entity_type] += 1
            return text

        def validate(self, params: Dict = None) -> None:
            pass

        def operator_name(self) -> str:
            return "entity_counter"

        def operator_type(self) -> OperatorType:
            return OperatorType.Anonymize

    return InstanceCounterAnonymizer


def create_reverser_operator(operator_type: OperatorType) -> Type[Operator]:
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
