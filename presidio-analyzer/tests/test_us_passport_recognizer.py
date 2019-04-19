from unittest import TestCase

from assertions import assert_result_within_score_range
from analyzer.predefined_recognizers import UsPassportRecognizer

us_passport_recognizer = UsPassportRecognizer()
entities = ["US_PASSPORT"]


class TestUsPassportRecognizer(TestCase):

    def test_valid_us_passport_no_context(self):
        num = '912803456'
        results = us_passport_recognizer.analyze(num, entities)

        assert len(results) == 1
        assert results[0].score != 0
        assert_result_within_score_range(results[0], entities[0], 0, 9, 0, 0.1)

    #  Task #603: Support keyphrases: Should pass after handling keyphrases, e.g. "travel document" or "travel permit"

    # def test_valid_us_passport_with_exact_context_phrase():
    #     num = '912803456'
    #     context = 'my travel document number is '
    #     results = us_passport_recognizer.analyze(context + num, entities)
    #
    #     assert len(results) == 1
    #     assert results[0].text = num
    #     assert results[0].score
    #
