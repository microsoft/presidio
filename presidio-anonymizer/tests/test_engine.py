from unittest.mock import Mock

from presidio_anonymizer.anonymizer_engine import AnonymizerEngine
from presidio_anonymizer.entities import AnalyzerResult
from presidio_anonymizer.entities.anonymizer_dto import AnonymizerDTO


def test_given_several_anonymizers_then_we_use_the_correct_one():
    mock = Mock()
    analyzer_results = Mock()
    analyzer_result = AnalyzerResult(
        {"score": 0.5, "entity_type": "PHONE_NUMBER", "start": 8, "end": 18}
    )
    anonymizer_dto = AnonymizerDTO("replace", {})
    anonymizer_dto.anonymizer_class = Anonymizer
    mock.get_anonymizers_dto = lambda: {"PHONE_NUMBER": anonymizer_dto}
    analyzer_results.to_sorted_unique_results = lambda reverse: [analyzer_result]
    mock.get_analysis_results = lambda: analyzer_results
    text = AnonymizerEngine().anonymize("Number: 0554555556", mock)
    assert text == "Number: I am your new text!"


class Anonymizer:
    def anonymize(self, text: str, params: dict = None):
        return "I am your new text!"

    def validate(self, params):
        pass


def get_anonymizer_dto(arg):
    assert arg == "anonymizer"
    return Anonymizer
