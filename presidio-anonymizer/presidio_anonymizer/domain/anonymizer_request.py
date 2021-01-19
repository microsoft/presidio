"""Validate and replace the json from the user request to object."""
from presidio_anonymizer.domain.analyzer_result import AnalyzerResult
from presidio_anonymizer.domain.analyzer_results import AnalyzerResults
from presidio_anonymizer.domain.invalid_exception import InvalidJsonException


class AnonymizerRequest(dict):
    """
    Validate and get three data entities from the user request.

    - text - the text we are working on.
    - transformations - the transformations we would like to make on the text.
    the default is replace.
    - analyzer_results - the results we received from the analyzer recognizer.
    """

    @classmethod
    def validate_and_convert(cls, content):
        """
        Validate the user input contains what we need and convert it to dictionary.

        :param content: the json from the user request.
        :return: AnonymizerRequest (dictionary)
        """
        cls.__validate_fields(content)
        cls = {"text": content.get("text"),
               "transformations": content.get("transformations"),
               "analyzer_results": AnalyzerResults()}

        for result in content.get("analyzer_results"):
            cls.get("analyzer_results").append(
                AnalyzerResult.validate_and_create(result))
        return cls

    @classmethod
    def __validate_fields(cls, content):
        if not content.get("analyzer_results"):
            raise InvalidJsonException("Invalid json, "
                                       "analyzer results can not be empty")
        if not content.get("text"):
            raise InvalidJsonException("Invalid json, text can not be empty")
