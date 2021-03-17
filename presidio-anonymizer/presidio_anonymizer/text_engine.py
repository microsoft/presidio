import logging
from typing import List, Dict

from presidio_anonymizer.entities.engine.operator_metadata import OperatorMetadata
from presidio_anonymizer.entities.engine.result.engine_result import \
    EngineResult
from presidio_anonymizer.entities.engine.result.result_item_builder import \
    ResultItemBuilder
from presidio_anonymizer.entities.engine.text_metadata import \
    TextMetadata
from presidio_anonymizer.operators.operators_factory import OperatorsFactory
from presidio_anonymizer.services.text_interpolator import TextInterpolator


class TextEngine:

    def __init__(self):
        self.logger = logging.getLogger("presidio-anonymizer")
        self.operators_factory = OperatorsFactory()

    def operate(self, text: str,
                text_metadata: List[TextMetadata],
                operators_metadata: Dict[
                    str, OperatorMetadata]) -> EngineResult:
        text_interpolator = TextInterpolator(original_text=text)
        manipulation_result = EngineResult()
        for manipulation in sorted(text_metadata, reverse=True):
            text_to_manipulate = text_interpolator.get_text_in_position(
                manipulation.start, manipulation.end
            )

            self.logger.debug(
                f"performing manipulation {manipulation}"
            )
            operator_metadata = self.__get_entity_operator_metadata(
                manipulation.entity_type, operators_metadata)
            manipulated_text = self.__manipulate_text(
                manipulation, text_to_manipulate, operator_metadata
            )
            index_from_end = text_interpolator.replace_text_get_insertion_index(
                manipulated_text, manipulation.start, manipulation.end
            )

            # The following creates an intermediate list of result entities,
            # ordered from end to start, and the indexes will be normalized
            # from start to end once the loop ends and the text length is deterministic.
            result_item_builder = ResultItemBuilder(operator_metadata.operator_type)
            result_item = result_item_builder.set_operator_name(
                operator_metadata.operator_name).set_entity_type(
                manipulation.entity_type).set_end(
                index_from_end).manipulated_text(manipulated_text).build()
            manipulation_result.add_item(result_item)

        manipulation_result.set_text(text_interpolator.output_text)
        manipulation_result.normalize_item_indexes()
        return manipulation_result

    def __manipulate_text(
            self,
            text_metadata: TextMetadata,
            text_to_manipulate: str,
            operator_metadata: OperatorMetadata
    ) -> str:
        entity_type = text_metadata.entity_type
        self.logger.debug(f"getting operator for {entity_type}")
        operator = self.operators_factory.create_operator_class(
            operator_metadata.operator_name, operator_metadata.operator_type)
        self.logger.debug(f"validating operator {operator} for {entity_type}")
        operator.validate(params=operator_metadata.params)
        params = operator_metadata.params
        params["entity_type"] = entity_type
        self.logger.debug(f"operating on {entity_type} with {operator}")
        anonymized_text = operator.operate(params=params, text=text_to_manipulate)
        return anonymized_text

    @staticmethod
    def __get_entity_operator_metadata(
            entity_type: str, operators_metadata: Dict[str, OperatorMetadata] = {}
    ) -> OperatorMetadata:
        # We try to get the anonymizer from the list by entity_type.
        # If it does not exist, we get the default from the list.
        anonymizer = operators_metadata.get(entity_type)
        if anonymizer:
            return anonymizer
        else:
            return operators_metadata.get("DEFAULT")
