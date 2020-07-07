from unittest import TestCase

from assertions import assert_result
from presidio_analyzer.predefined_recognizers import INDPANRecognizer

ind_pan_recognizer = INDPANRecognizer()
entities = ["pan"]


class TestINDPANRecognizer(TestCase):

    def test_valid_pan(self):
        num = 'ABCBF1234F'
        results = ind_pan_recognizer.analyze(num, entities)
        assert len(results) == 1

    def test_invalid_pan(self):
        num = 'ABCQF1234F'
        results = ind_pan_recognizer.analyze(num, entities)
        assert len(results) == 0