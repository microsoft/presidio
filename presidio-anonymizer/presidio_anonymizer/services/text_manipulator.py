import logging
from typing import List

from presidio_anonymizer.entities.manipulator.manipulated_entity import \
    ManipulatedEntity
from presidio_anonymizer.entities.manipulator.manipulated_result import \
    ManipulatedResult
from presidio_anonymizer.entities.manipulator.text_manipulation_data import \
    TextManipulationData
from presidio_anonymizer.services.text_builder import TextBuilder


class TextManipulator:
    logger = logging.getLogger("presidio-anonymizer")

    def manipulate_text(self, text: str,
                        manipulations: List[TextManipulationData]) -> ManipulatedResult:
        text_builder = TextBuilder(original_text=text)
        manipulation_result = ManipulatedResult()
        for manipulation in sorted(manipulations, reverse=True):
            text_to_manipulate = text_builder.get_text_in_position(
                manipulation.start, manipulation.end
            )

            self.logger.debug(
                f"performing manipulation {manipulation}"
            )

            manipulated_text = self.__manipulate_text(
                manipulation, text_to_manipulate
            )
            index_from_end = text_builder.replace_text_get_insertion_index(
                manipulated_text, manipulation.start, manipulation.end
            )

            # The following creates an intermediate list of anonymized entities,
            # ordered from end to start, and the indexes will be normalized
            # from start to end once the loop ends and the text length is deterministic.
            result_item = ManipulatedEntity(
                manipulator=manipulation.manipulator_class().manipulator_name(),
                entity_type=manipulation.entity_type,
                start=0,
                end=index_from_end,
                anonymized_text=manipulated_text,
            )

            manipulation_result.add_item(result_item)

        manipulation_result.set_text(text_builder.output_text)
        manipulation_result.normalize_item_indexes()
        return manipulation_result

    def __manipulate_text(
            self,
            manipulator_entity: TextManipulationData,
            text_to_anonymize: str,
    ) -> str:
        entity_type = manipulator_entity.entity_type
        self.logger.debug(f"getting manipulator for {entity_type}")
        manipulator = manipulator_entity.manipulator_class()
        self.logger.debug(f"validating manipulator {manipulator} for {entity_type}")
        manipulator.validate(params=manipulator_entity.params)
        params = manipulator_entity.params
        params["entity_type"] = entity_type
        self.logger.debug(f"anonymizing {entity_type} with {manipulator}")
        anonymized_text = manipulator.manipulate(params=params, text=text_to_anonymize)
        return anonymized_text
