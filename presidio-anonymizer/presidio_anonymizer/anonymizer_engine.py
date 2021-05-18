"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
import logging
from typing import List, Dict, Optional

from presidio_anonymizer.core.engine_base import EngineBase
from presidio_anonymizer.entities.engine import OperatorConfig
from presidio_anonymizer.entities.engine import RecognizerResult
from presidio_anonymizer.entities.engine.result import EngineResult
from presidio_anonymizer.operators import OperatorType

DEFAULT = "replace"


class AnonymizerEngine(EngineBase):
    """
    AnonymizerEngine class.

    Handles the entire logic of the Presidio-anonymizer. Gets the original text
    and replaces the PII entities with the desired anonymizers.
    """

    logger = logging.getLogger("presidio-anonymizer")

    def __init__(self):
        EngineBase.__init__(self)

    def anonymize(
            self,
            text: str,
            analyzer_results: List[RecognizerResult],
            operators: Optional[Dict[str, OperatorConfig]] = None
    ) -> EngineResult:
        """Anonymize method to anonymize the given text.

        :param text: the text we are anonymizing
        :param analyzer_results: A list of RecognizerResult class -> The results we
        received from the analyzer
        :param operators: The configuration of the anonymizers we would like
        to use for each entity e.g.: {"PHONE_NUMBER":OperatorConfig("redact", {})}
        received from the analyzer
        :return: the anonymized text and a list of information about the
        anonymized entities.
        """
        analyzer_results = self._remove_conflicts_and_get_text_manipulation_data(
            analyzer_results)

        operators = self.__check_or_add_default_operator(operators)

        return self._operate(text, analyzer_results, operators, OperatorType.Anonymize)

    def _remove_conflicts_and_get_text_manipulation_data(self, analyzer_results: List[
            RecognizerResult]) -> List[RecognizerResult]:
        """
        Iterate the list and create a sorted unique results list from it.

        Only insert results which are:
        1. Indices are not contained in other result.
        2. Have the same indices as other results but with larger score.
        :return: List
        """
        unique_text_metadata_elements = []
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
                unique_text_metadata_elements.append(result)
            else:
                self.logger.debug(
                    f"removing element {result} from results list due to conflict"
                )
        return unique_text_metadata_elements

    def get_anonymizers(self) -> List[str]:
        """Return a list of supported anonymizers."""
        names = [p for p in self.operators_factory.get_anonymizers().keys()]
        return names

    @staticmethod
    def __is_result_conflicted_with_other_elements(other_elements, result):
        return any([result.has_conflict(other_element) for other_element in
                    other_elements])

    @staticmethod
    def __check_or_add_default_operator(operators: Dict[
        str, OperatorConfig]) -> \
            Dict[str, OperatorConfig]:
        default_operator = OperatorConfig(DEFAULT)
        if not operators:
            return {"DEFAULT": default_operator}
        if not operators.get("DEFAULT"):
            operators["DEFAULT"] = default_operator
        return operators
