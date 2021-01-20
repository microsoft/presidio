"""
Engine request entity.

It get the data and validate it before the engine receives it.
"""
import logging

from presidio_anonymizer.anonymizers.fpe import FPE
from presidio_anonymizer.anonymizers.hash import Hash
from presidio_anonymizer.anonymizers.mask import Mask
from presidio_anonymizer.anonymizers.redact import Redact
from presidio_anonymizer.anonymizers.replace import Replace
from presidio_anonymizer.entities.analyzer_result import AnalyzerResult
from presidio_anonymizer.entities.analyzer_results import AnalyzerResults
from presidio_anonymizer.entities.invalid_exception import InvalidParamException


class AnonymizerEngineRequest:
    """The request the engine will get and act on."""

    anonymizers = {"mask": Mask, "fpe": FPE, "replace": Replace, "hash": Hash,
                   "redact": Redact}

    logger = logging.getLogger("presidio-anonymizer")

    def __init__(self,
                 data: dict):
        """Handle text replacement for PIIs with requested transformations.

        :param data: a map which contains the transformations, analyzer_results and text
        """
        self._transformations = {}
        self._analysis_results = AnalyzerResults()
        self.__validate_and_insert_input(data)

    def get_transformations(self):
        """Get the transformations data."""
        return self._transformations

    def get_transformation(self, analyzer_result: AnalyzerResult):
        """
        Get the right transformation from the list.

        When transformation does not exist, we fall back to default.
        :param analyzer_result: the result we are going to do the transformation on
        :return: transformation
        """
        transformation = self.get(analyzer_result.entity_type)
        if not transformation:
            transformation = self.get("default")
            if not transformation:
                new_val = f"<{analyzer_result.entity_type}>"
                return {"type": "replace", "new_value": new_val, "anonymizer": Replace}
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
        results = data.get("analyzer_results")
        if results is None or len(results) == 0:
            raise InvalidParamException("Invalid input, "
                                        "analyzer results can not be empty")
        for result in results:
            self._analysis_results.append(
                AnalyzerResult.validate_and_create(result))

    def __handle_transformations(self, data):
        transformations = data.get("transformations")
        if transformations is not None:
            for key, transformation in transformations.items():
                anonymizer = self.__get_anonymizer(transformation)
                transformation["anonymizer"] = anonymizer
                self._transformations[key] = transformation

    def __handle_text(self, data):
        self._text = data.get("text")
        if self._text == "" or self._text is None:
            raise InvalidParamException("Invalid input, text can not be empty")
        self._end_point = len(self._text)

    def __get_anonymizer(self, transformation):
        anonymizer_type = transformation.get("type").lower()
        anonymizer_class = self.anonymizers.get(anonymizer_type)
        if anonymizer_class is None:
            self.logger.error(f"No such anonimyzer class {anonymizer_type}")
            raise InvalidParamException(
                f"Invalid anonymizer class '{anonymizer_type}'.")
        return anonymizer_class
