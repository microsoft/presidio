"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
import logging

from presidio_anonymizer.anonymizers.fpe import FPE
from presidio_anonymizer.anonymizers.hash import Hash
from presidio_anonymizer.anonymizers.mask import Mask
from presidio_anonymizer.anonymizers.redact import Redact
from presidio_anonymizer.anonymizers.replace import Replace
from presidio_anonymizer.domain.invalid_exception import InvalidParamException
from presidio_anonymizer.domain.transformations import Transformations

anonymizers = {"mask": Mask, "fpe": FPE, "replace": Replace, "hash": Hash,
               "redact": Redact}
logger = logging.getLogger("presidio-anonymizer")


class AnonymizerEngine:
    """
    AnonymizerEngine class.

    Handles the entire logic of the Presidio-anonymizer. Gets the original text
    and replaces the PII entities with the desired transformations.
    """

    def __init__(
            self,
            data: dict,
    ):
        """Handle text replacement for PIIs with requested transformations.

        :param data: a map which contains the transformations, analyzer_results and text
        """
        transformations = data.get("transformations")
        if transformations is None:
            transformations = {}
        self._transformations = Transformations(transformations)
        self._analysis_results = data.get("analyzer_results")
        self._text = data.get("text")
        if self._text is None:
            self._text = ""
        self._end_point = len(self._text)

    def anonymize(self):
        """Anonymize method to anonymize the given text.

        :return: the anonymized text
        """
        self.__validate_input()
        analyzer_results = self._analysis_results.to_sorted_set(True)
        for result in analyzer_results:
            transformation = self._transformations.get_transformation(result)
            logger.debug(f"received transformation {transformation.get('type')}")
            anonymizer_class = transformation.get("anonymizer")
            new_text = anonymizer_class().anonymize(transformation)
            self.__replace(result.start, result.end, new_text)
        return self._text

    def __get_anonymizer(self, transformation):
        anonymizer_type = transformation.get("type").lower()
        anonymizer_class = anonymizers.get(anonymizer_type)
        if anonymizer_class is None:
            logger.error(f"No such anonimyzer class {anonymizer_type}")
            raise InvalidParamException(
                f"Invalid anonymizer class '{anonymizer_type}'.")
        return anonymizer_class

    def __replace(self, start, end, new_text):
        end_of_text = min(end, self._end_point)
        self._text = self._text[:start] + new_text + self._text[end_of_text:]
        self._end_point = start

    def __validate_input(self):
        if self._analysis_results is None or len(self._analysis_results) == 0:
            raise InvalidParamException("Analyze results must contain data.")
        for key, transformation in self._transformations.items():
            anonymizer = self.__get_anonymizer(transformation)
            transformation["anonymizer"] = anonymizer
            self._transformations[key] = transformation
        if self._text == "" or self._text is None:
            raise InvalidParamException("Please insert a valid text.")
