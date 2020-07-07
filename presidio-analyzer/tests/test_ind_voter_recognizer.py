from unittest import TestCase

from assertions import assert_result
from presidio_analyzer.predefined_recognizers import INDEPICRecognizer

ind_epic_recognizer = INDEPICRecognizer()
entities = ["voter"]


class TestINDEPICRecognizer(TestCase):

    def test_valid_voter(self):
        num = 'ABC1234567'
        results = ind_epic_recognizer.analyze(num, entities)
        assert len(results) == 1

    def test_invalid_voter(self):
        num = 'ABC12345678'
        results = ind_epic_recognizer.analyze(num, entities)
        assert len(results) == 0