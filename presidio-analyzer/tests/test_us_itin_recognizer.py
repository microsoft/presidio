from unittest import TestCase

from assertions import assert_result_within_score_range
from analyzer.predefined_recognizers import UsItinRecognizer

us_itin_recognizer = UsItinRecognizer()
entities = ["US_ITIN"]


class TestUsItinRecognizer(TestCase):

    def test_valid_us_itin_very_weak_match(self):
        num1 = '911-701234'
        num2 = '91170-1234'
        results = us_itin_recognizer.analyze(
            '{} {}'.format(num1, num2), entities)

        assert len(results) == 2

        assert results[0].score != 0
        assert_result_within_score_range(
            results[0], entities[0], 0, 10, 0, 0.3)

        assert results[1].score != 0
        assert_result_within_score_range(
            results[1], entities[0], 11, 21, 0, 0.3)

    def test_valid_us_itin_weak_match(self):
        num = '911701234'
        results = us_itin_recognizer.analyze(num, entities)

        assert len(results) == 1
        assert_result_within_score_range(
            results[0], entities[0], 0, 9, 0.3, 0.4)

    def test_valid_us_itin_medium_match(self):
        num = '911-70-1234'
        results = us_itin_recognizer.analyze(num, entities)

        assert len(results) == 1
        assert_result_within_score_range(
            results[0], entities[0], 0, 11, 0.5, 0.6)

    def test_invalid_us_itin(self):
        num = '911-89-1234'
        results = us_itin_recognizer.analyze(num, entities)

        assert len(results) == 0

    def test_invalid_us_itin_exact_context(self):
        num = '911-89-1234'
        context = "my taxpayer id"
        results = us_itin_recognizer.analyze(
            '{} {}'.format(context, num), entities)

        assert len(results) == 0
