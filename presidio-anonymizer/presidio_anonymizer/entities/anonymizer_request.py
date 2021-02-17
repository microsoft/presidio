"""
Engine request entity.

It get the data and validate it before the engine receives it.
"""
import logging

from presidio_anonymizer.entities import AnalyzerResult
from presidio_anonymizer.entities import AnalyzerResults
from presidio_anonymizer.entities import InvalidParamException
from presidio_anonymizer.entities.anonymizer_dto import AnonymizerDTO


class AnonymizerRequest:
    """Input validation for the anonymize process."""

    logger = logging.getLogger("presidio-anonymizer")

    def __init__(self, data: dict):
        """Handle and validate data for the text replacement.

        :param data: a map which contains the anonymizers, analyzer_results and text
        """
        self._anonymizers_dto = {}
        self._analysis_results = AnalyzerResults()
        self.__validate_and_insert_input(data)

    def get_analysis_results(self):
        """Get the analysis results."""
        return self._analysis_results

    def get_anonymizers_dto(self):
        """Get the anonymizers data transfer objects."""
        return self._anonymizers_dto

    def __validate_and_insert_input(self, data: dict):
        self.__handle_text(data)
        self.__handle_analyzer_results(data)
        self.__handle_anonymizers(data)

    def __handle_analyzer_results(self, data):
        """
        Go over analyzer results, check they are valid and convert to AnalyzeResult.

        :param data: contains the text, anonymizers and analyzer_results
        :return: None
        """
        analyzer_results = data.get("analyzer_results")
        if not analyzer_results:
            self.logger.debug("invalid input, json missing field: analyzer_results")
            raise InvalidParamException(
                "Invalid input, " "analyzer results can not be empty"
            )
        text_len = len(data.get("text"))
        for analyzer_result in analyzer_results:
            analyzer_result = AnalyzerResult(analyzer_result)
            analyzer_result.validate_position_in_text(text_len)
            self._analysis_results.append(analyzer_result)

    def __handle_anonymizers(self, data):
        """
        Go over the anonymizers and get the relevant anonymizer class for it.

        Inserts the class to the anonymizer so the engine will use it.
        :param data: contains the text, anonymizers and analyzer_results
        :return: None
        """
        anonymizers = data.get("anonymizers")
        if anonymizers is not None:
            for key, anonymizer_json in anonymizers.items():
                self.logger.debug(
                    f"converting {anonymizer_json} to anonymizer dto class")
                anonymizer_dto = AnonymizerDTO.from_json(anonymizer_json)
                self._anonymizers_dto[key] = anonymizer_dto

    def __handle_text(self, data):
        self._text = data.get("text")
        if not self._text:
            self.logger.debug("invalid input, json is missing text field")
            raise InvalidParamException("Invalid input, text can not be empty")
