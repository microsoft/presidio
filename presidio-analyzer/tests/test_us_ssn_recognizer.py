from unittest import TestCase

from assertions import assert_result, assert_result_within_score_range
from analyzer.predefined_recognizers import UsSsnRecognizer

us_ssn_recognizer = UsSsnRecognizer()
entities = ["US_SSN"]


class TestUsSsnRecognizer(TestCase):

    def test_valid_us_ssn_very_weak_match(self):
        num1 = '078-051120'
        num2 = '07805-1120'
        results = us_ssn_recognizer.analyze(
            '{} {}'.format(num1, num2), entities)

        assert len(results) == 2

        assert results[0].score != 0
        assert_result_within_score_range(
            results[0], entities[0], 0, 10, 0, 0.3)

        assert results[0].score != 0
        assert_result_within_score_range(
            results[1], entities[0], 11, 21, 0, 0.3)

    def test_valid_us_ssn_weak_match(self):
        num = '078051120'
        results = us_ssn_recognizer.analyze(num, entities)

        assert len(results) == 1
        assert results[0].score != 0
        assert_result_within_score_range(
            results[0], entities[0], 0, 9, 0.3, 0.4)

    def test_valid_us_ssn_medium_match(self):
        num = '078-05-1120'
        results = us_ssn_recognizer.analyze(num, entities)

        assert len(results) == 1
        assert results[0].score != 0
        assert_result_within_score_range(
            results[0], entities[0], 0, 11, 0.5, 0.6)
        assert 0.49 < results[0].score < 0.6

    def test_invalid_us_ssn(self):
        num = '078-05-11201'
        results = us_ssn_recognizer.analyze(num, entities)

        assert len(results) == 0
