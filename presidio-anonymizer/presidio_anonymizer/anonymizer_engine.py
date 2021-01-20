"""Handles the entire logic of the Presidio-anonymizer and text anonymizing."""
from domain import AnalyzerResults
from presidio_anonymizer.domain.transformations import Transformations
from presidio_anonymizer.anonymizers.fpe import FPE
from presidio_anonymizer.anonymizers.mask import Mask
from presidio_anonymizer.anonymizers.replace import Replace

anonymizers = {"mask": Mask, "fpe": FPE, "replace": Replace}


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
        self._transformations = Transformations(data.get("transformations"))
        self._analyze_results = data.get("analyzer_results")
        if self._analyze_results is None:
            self._analyze_results = AnalyzerResults()
        self._text = data.get("text")
        if self._text is None:
            self._text = ""
        self._end_point = len(self._text)

    def anonymize(self):
        """Anonymize method to anonymize the given text.

        :return: the anonymized text
        """
        analyzer_results = self._analyze_results.to_sorted_set(True)
        for result in analyzer_results:
            transformation = self._transformations.get_transformation(result)
            anonymizer_class = anonymizers.get(transformation.get("type").lower())

            new_text = anonymizer_class().anonymize(transformation)
            self.__replace(result.start, result.end, new_text)
        return self._text

    def __replace(self, start, end, new_text):
        end_of_text = min(end, self._end_point)
        self._text = self._text[:start] + new_text + self._text[end_of_text:]
        self._end_point = start
