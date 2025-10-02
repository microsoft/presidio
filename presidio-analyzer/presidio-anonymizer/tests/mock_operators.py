from typing import Type, Dict

from presidio_anonymizer.operators import OperatorType, Operator


def create_instance_counter_anonymizer() -> Type[Operator]:
    class InstanceCounterAnonymizer(Operator):
        """
        Anonymizer which replaces the entity value
        with an instance counter per entity.
        """

        REPLACING_FORMAT = "<{entity_type}_{index}>"

        def operate(self, text: str, params: Dict = None) -> str:
            """Anonymize the input text."""

            entity_type: str = params["entity_type"]

            # entity_mapping is a dict of dicts containing mappings per entity type
            entity_mapping: Dict[Dict:str] = params["entity_mapping"]

            entity_mapping_for_type = entity_mapping.get(entity_type)
            if not entity_mapping_for_type:
                new_text = self.REPLACING_FORMAT.format(
                    entity_type=entity_type, index=0
                )
                entity_mapping[entity_type] = {}

            else:
                if text in entity_mapping_for_type:
                    return entity_mapping_for_type[text]

                previous_index = self._get_last_index(entity_mapping_for_type)
                new_text = self.REPLACING_FORMAT.format(
                    entity_type=entity_type, index=previous_index + 1
                )

            entity_mapping[entity_type][text] = new_text
            return new_text

        @staticmethod
        def _get_last_index(entity_mapping_for_type: Dict) -> int:
            """Get the last index for a given entity type."""

            def get_index(value: str) -> int:
                return int(value.split("_")[-1][:-1])

            indices = [get_index(v) for v in entity_mapping_for_type.values()]
            return max(indices)

        def validate(self, params: Dict = None) -> None:
            """Validate operator parameters."""

            if "entity_mapping" not in params:
                raise ValueError("An input Dict called `entity_mapping` is required.")
            if "entity_type" not in params:
                raise ValueError("An entity_type param is required.")

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
