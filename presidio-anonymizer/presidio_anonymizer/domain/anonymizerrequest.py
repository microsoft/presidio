from presidio_anonymizer.domain.analyzer_result import AnalyzerResult
from presidio_anonymizer.domain.analyzer_results import AnalyzerResults
from presidio_anonymizer.domain.invalid_exception import InvalidJsonException


# TODO change to anonymize request
class AnonymizerRequest(dict):

    @classmethod
    def validate_and_convert(cls, content):
        cls.__validate_fields(content)
        cls = {"text": content.get("text"),
               "transformations": content.get("transformations"),
               "analyzer_results": AnalyzerResults()}

        for result in content.get("analyzer_results"):
            cls.get("analyzer_results").append_result(
                AnalyzerResult.validate_and_convert(result))
        return cls

    @classmethod
    def __validate_fields(cls, content):
        if not content.get("analyzer_results"):
            raise InvalidJsonException("Invalid json, analyzer results can not be empty")
        if not content.get("text"):
            raise InvalidJsonException("Invalid json, text can not be empty")
