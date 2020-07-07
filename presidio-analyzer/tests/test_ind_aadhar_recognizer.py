from unittest import TestCase

from assertions import assert_result
from presidio_analyzer.predefined_recognizers import INDAadharRecognizer

ind_aadhar_recognizer = INDAadharRecognizer()
entities = ["aadhar"]


class TestINDAadharRecognizer(TestCase):

    def test_valid_aadhar(self):
        num = '8547 5897 5874'
        results = ind_aadhar_recognizer.analyze(num, entities)
        assert len(results) == 1

    def test_invalid_aadhar(self):
        num = '12345 67485 47459'
        results = ind_aadhar_recognizer.analyze(num, entities)
        assert len(results) == 0