from unittest import TestCase

from assertions import assert_result
from analyzer.predefined_recognizers import NhsRecognizer
from analyzer.entity_recognizer import EntityRecognizer

nhs_recognizer = NhsRecognizer()
entities = ["UK_NHS"]


class TestNhsRecognizer(TestCase):

    def test_valid_uk_nhs_with_dashes(self):
        num = '401-023-2137'
        results = nhs_recognizer.analyze(num, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 12, 1.0)

    def test_valid_uk_nhs_with_spaces(self):
        num = '221 395 1837'
        results = nhs_recognizer.analyze(num, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 12, 1.0)

    def test_valid_uk_nhs_with_no_delimeters(self):
        num = '0032698674'
        results = nhs_recognizer.analyze(num, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 10, 1.0)

    def test_invalid_uk_nhs(self):
        num = '401-023-2138'
        results = nhs_recognizer.analyze(num, entities)

        assert len(results) == 0
