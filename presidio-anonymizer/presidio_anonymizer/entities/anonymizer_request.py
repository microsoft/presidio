"""
Engine request entity.

It get the data and validate it before the engine receives it.
"""
import logging

from presidio_anonymizer.entities import AnalyzerResult
from presidio_anonymizer.entities import AnalyzerResults
from presidio_anonymizer.entities import InvalidParamException


class AnonymizerRequest:
    """Input validation for the anonymize process."""

    logger = logging.getLogger("presidio-anonymizer")

    def __init__(self, data: dict, anonymizers):
        """Handle and validate data for the text replacement.

        :param data: a map which contains the transformations, analyzer_results and text
        """
        self.anonymizers = anonymizers
        self._transformations = {}
        self._analysis_results = AnalyzerResults()
        self.__validate_and_insert_input(data)
        self.default_transformation = {
            "type": "replace",
            "anonymizer": self.anonymizers["replace"],
        }

    def get_transformation(self, entity_type: str):
        """
        Get the right transformation from the list.

        When transformation does not exist, we fall back to default.
        :param analyzer_result: the result we are going to do the transformation on
        :return: transformation
        """
        transformation = self._transformations.get(entity_type)
        if not transformation:
            transformation = self._transformations.get("DEFAULT")
            if not transformation:
                transformation = self.default_transformation
        transformation["entity_type"] = entity_type
        return transformation

    def get_text(self):
        """Get the text we are working on."""
        return self._text

    def get_analysis_results(self):
        """Get the analysis results."""
        return self._analysis_results

    def __validate_and_insert_input(self, data: dict):
        self.__handle_analyzer_results(data)
        self.__handle_text(data)
        self.__handle_transformations(data)

    def __handle_analyzer_results(self, data):
        """
        Go over analyzer results, check they are valid and convert to AnalyzeResult.

        :param data: contains the text, transformations and analyzer_results
        :return: None
        """
        analyzer_results = data.get("analyzer_results")
        if not analyzer_results:
            self.logger.debug("invalid input, json missing field: analyzer_results")
            raise InvalidParamException(
                "Invalid input, " "analyzer results can not be empty"
            )
        for analyzer_result in analyzer_results:
            self._analysis_results.append(AnalyzerResult(analyzer_result))

    def __handle_transformations(self, data):
        """
        Go over the transformations and get the relevant anonymizer class for it.

        Inserts the class to the transformation so the engine will use it.
        :param data: contains the text, transformations and analyzer_results
        :return: None
        """
        transformations = data.get("transformations")
        if transformations is not None:
            for key, transformation in transformations.items():
                self.logger.debug(f"converting {transformation} to anonymizer class")
                anonymizer = self.__get_anonymizer(transformation)
                self.logger.debug(f"applying class {anonymizer} to {transformation}")
                transformation["anonymizer"] = anonymizer
                self._transformations[key] = transformation

    def __handle_text(self, data):
        self._text = data.get("text")
        if not self._text:
            self.logger.debug("invalid input, json is missing text field")
            raise InvalidParamException("Invalid input, text can not be empty")

    def __get_anonymizer(self, transformation):
        """
        Extract the anonymizer class from the anonymizers list.

        :param transformation: a single transformation value
        :return: Anonymizer
        """
        anonymizer_type = transformation.get("type").lower()
        anonymizer = self.anonymizers.get(anonymizer_type)
        if not anonymizer:
            self.logger.error(f"No such anonymizer class {anonymizer_type}")
            raise InvalidParamException(
                f"Invalid anonymizer class '{anonymizer_type}'."
            )
        return anonymizer
