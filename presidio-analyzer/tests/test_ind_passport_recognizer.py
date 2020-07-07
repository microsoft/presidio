from unittest import TestCase

from assertions import assert_result
from presidio_analyzer.predefined_recognizers import INDPassportRecognizer

ind_passport_recognizer = INDPassportRecognizer()
entities = ["passport"]


class TestINDPassportRecognizer(TestCase):

    def test_valid_passport(self):
        num = 'A1234567'
        results = ind_passport_recognizer.analyze(num, entities)
        assert len(results) == 1

    def test_invalid_passport(self):
        num = 'A123456F'
        results = ind_passport_recognizer.analyze(num, entities)
        assert len(results) == 0