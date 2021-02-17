from unittest.mock import Mock

from presidio_anonymizer.anonymizer_engine import AnonymizerEngine
from presidio_anonymizer.entities import AnalyzerResult


def test_given_several_anonymizers_then_we_use_the_correct_one():
    anonymizer = Mock()
    anonymizer.get = get_anonymizer_dto
    mock = Mock()
    mock.get_text = lambda: "Number: 0554555556"
    analyzer_results = Mock()
    analyzer_result = AnalyzerResult(
        {"score": 0.5, "entity_type": "PHONE_NUMBER", "start": 8, "end": 18}
    )
    analyzer_results.to_sorted_unique_results = lambda reverse: [analyzer_result]
    mock.get_analysis_results = lambda: analyzer_results
    mock.get_anonymizer_dto = lambda result: anonymizer
    text = AnonymizerEngine().anonymize(mock)
    assert text == "Number: I am your new text!"


class Anonymizer:
    def anonymize(self, text, params):
        return "I am your new text!"

    def validate(self, params):
        pass


def get_anonymizer_dto(arg):
    assert arg == "anonymizer"
    return Anonymizer
