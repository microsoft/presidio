"""
Engine request entity.

It get the data and validate it before the engine receives it.
"""
import logging
from typing import List, Dict

from presidio_anonymizer.entities import AnalyzerResult
from presidio_anonymizer.entities import AnalyzerResults
from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.anonymizer_config import AnonymizerConfig


class AnonymizerRequest:
    """Input validation for the anonymize process."""

    logger = logging.getLogger("presidio-anonymizer")

    @classmethod
    def handle_analyzer_results_json(cls, data: Dict) -> List[AnalyzerResult]:
        """
        Go over analyzer results, validate them and convert to List[AnalyzeResult].

        :param data: contains the anonymizers and analyzer_results_json
        """
        analyzer_results = AnalyzerResults()
        analyzer_results_json = data.get("analyzer_results")
        if not analyzer_results_json:
            cls.logger.debug(
                "invalid input, json missing field: analyzer_results_json")
            raise InvalidParamException(
                "Invalid input, " "analyzer results can not be empty"
            )
        for analyzer_result in analyzer_results_json:
            analyzer_result = AnalyzerResult.from_json(analyzer_result)
            analyzer_results.append(analyzer_result)
        return analyzer_results

    @classmethod
    def get_anonymizer_configs_from_json(cls, data: Dict) -> \
            Dict[str, AnonymizerConfig]:
        """
        Go over the anonymizers and get the relevant anonymizer class for it.

        Inserts the class to the anonymizer so the engine will use it.
        :param data: contains the text, configuration and analyzer_results
        value - AnonynmizerConfig
        """
        anonymizers_config = {}
        anonymizers = data.get("anonymizers")
        if anonymizers is not None:
            for key, anonymizer_json in anonymizers.items():
                cls.logger.debug(
                    f"converting {anonymizer_json} to anonymizer config class")
                anonymizer_config = AnonymizerConfig.from_json(anonymizer_json)
                anonymizers_config[key] = anonymizer_config
        return anonymizers_config
