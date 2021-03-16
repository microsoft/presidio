"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
import logging
from typing import List, Dict, Optional

from presidio_anonymizer.entities.engine.anonymize_result_item import \
    AnonymizeResultItem
from presidio_anonymizer.entities.engine.engine_result import EngineResult
from presidio_anonymizer.entities.manipulator.text_manipulation_item import \
    TextManipulationItem
from presidio_anonymizer.operators import Operator
from presidio_anonymizer.entities import (
    RecognizerResult,
    AnonymizerConfig,
)
from presidio_anonymizer.services.text_manipulator import TextManipulator

DEFAULT = "replace"


class AnonymizerEngine:
    """
    AnonymizerEngine class.

    Handles the entire logic of the Presidio-anonymizer. Gets the original text
    and replaces the PII entities with the desired anonymizers.
    """

    def __init__(self):
        self.logger = logging.getLogger("presidio-anonymizer")
        self.text_manipulator = TextManipulator()

    def anonymize(
            self,
            text: str,
            analyzer_results: List[RecognizerResult],
            anonymizers_config: Optional[Dict[str, AnonymizerConfig]] = None,
    ) -> EngineResult:
        """Anonymize method to anonymize the given text.

        :param text: the text we are anonymizing
        :param analyzer_results: A list of RecognizerResult class -> The results we
        received from the analyzer
        :param anonymizers_config: The configuration of the anonymizers we would like
        to use for each entity e.g.: {"PHONE_NUMBER":AnonymizerConfig("redact", {})}
        received from the analyzer
        :return: the anonymized text and a list of information
        about the anonymized entities.
        """
        manipulation_entities = self._remove_conflicts_and_get_text_manipulation_data(
            analyzer_results,
            anonymizers_config)

        manipulation_result = self.text_manipulator.manipulate_text(text,
                                                                manipulation_entities)
        engine_result = EngineResult(manipulation_result.text)
        for entity in manipulation_result.items:
            anonymized_entity = AnonymizeResultItem.from_manipulated_entity(entity)
            engine_result.append_item(anonymized_entity)
        return engine_result

    def _remove_conflicts_and_get_text_manipulation_data(self, analyzer_results,
                                                         anonymizers_config: Dict):
        """
        Iterate the list and create a sorted unique results list from it.

        Only insert results which are:
        1. Indices are not contained in other result.
        2. Have the same indices as other results but with larger score.
        :return: List
        """
        unique_manipulation_elements = []
        # This list contains all elements which we need to check a single result
        # against. If a result is dropped, it can also be dropped from this list
        # since it is intersecting with another result and we selected the other one.
        other_elements = analyzer_results.copy()
        for result in analyzer_results:
            other_elements.remove(result)
            result_conflicted = self.__is_result_conflicted_with_other_elements(
                other_elements, result)
            if not result_conflicted:
                other_elements.append(result)
                anonymizer = self.__get_anonymizer_config(result.entity_type,
                                                          anonymizers_config)
                manipulation_entity = TextManipulationItem.from_anonymizer_data(
                    result, anonymizer)
                unique_manipulation_elements.append(manipulation_entity)
            else:
                self.logger.debug(
                    f"removing element {result} from results list due to conflict"
                )
        return unique_manipulation_elements

    @staticmethod
    def get_anonymizers() -> List[str]:
        """Return a list of supported anonymizers."""
        names = [p for p in Operator.get_anonymizers().keys()]
        return names

    @staticmethod
    def __is_result_conflicted_with_other_elements(other_elements, result):
        return any([result.has_conflict(other_element) for other_element in
                    other_elements])

    @staticmethod
    def __get_anonymizer_config(
            entity_type: str, anonymizers_config: Dict[str, AnonymizerConfig] = {}
    ) -> AnonymizerConfig:
        # We try to get the anonymizer from the list by entity_type.
        # If it does not exist, we try to get the default from the list.
        # If there is no default we fallback into the current DEFAULT which is replace.
        if anonymizers_config:
            anonymizer = anonymizers_config.get(entity_type)
            if anonymizer:
                return anonymizer
            else:
                return anonymizers_config.get("DEFAULT")
        return AnonymizerConfig(DEFAULT, {})
