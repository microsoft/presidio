from unittest.mock import Mock

import pytest

from presidio_anonymizer.anonymizer_engine import AnonymizerEngine
from presidio_anonymizer.entities import AnalyzerResult, InvalidParamException


def test_given_shorter_text_from_analyzer_result_range_then_we_fail():
    transformation = Mock()
    transformation.get = get_transformation
    mock = Mock()
    mock.get_text = lambda: "Number"
    analyzer_results = Mock()
    analyzer_result = AnalyzerResult(
        {"score": 0.5, "entity_type": "PHONE_NUMBER", "start": 8, "end": 20}
    )
    analyzer_results.to_sorted_unique_results = lambda reverse: [analyzer_result]
    mock.get_analysis_results = lambda: analyzer_results
    mock.get_transformation = lambda result: transformation
    with pytest.raises(InvalidParamException) as e:
        AnonymizerEngine().anonymize(mock)
    assert (
            e.value.err_msg == "Invalid text position start with 8 and end with 20, "
                               "original text length is only 6."
    )


def test_given_several_transformations_then_we_use_the_correct_one():
    transformation = Mock()
    transformation.get = get_transformation
    mock = Mock()
    mock.get_text = lambda: "Number: 0554555556"
    analyzer_results = Mock()
    analyzer_result = AnalyzerResult(
        {"score": 0.5, "entity_type": "PHONE_NUMBER", "start": 8, "end": 18}
    )
    analyzer_results.to_sorted_unique_results = lambda reverse: [analyzer_result]
    mock.get_analysis_results = lambda: analyzer_results
    mock.get_transformation = lambda result: transformation
    text = AnonymizerEngine().anonymize(mock)
    assert text == "Number: I am your new text!"


class Anonymizer:
    def anonymize(self, text, params):
        return "I am your new text!"

    def validate(self, params):
        pass


def get_transformation(arg):
    assert arg == "anonymizer"
    return Anonymizer
