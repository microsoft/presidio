from unittest import TestCase

from assertions import assert_result
from presidio_analyzer.predefined_recognizers import INDPhoneRecognizer

ind_phone_recognizer = INDPhoneRecognizer()
entities = ["phone"]


class TestINDPhoneRecognizer(TestCase):

    def test_valid_phone(self):
        num = '(+91)9845787456'
        results = ind_phone_recognizer.analyze(num, entities)
        assert len(results) == 1

    def test_invalid_phone(self):
        num = '(+91)98457874567'
        results = ind_phone_recognizer.analyze(num, entities)
        assert len(results) == 0
    
    def test_valid_phone2(self):
        num = '+91-033-1234-5678'
        results = ind_phone_recognizer.analyze(num, entities)
        assert len(results) == 1
        
    def test_invalid_phone2(self):
        num = '+91-033-1234-56787'
        results = ind_phone_recognizer.analyze(num, entities)
        assert len(results) == 0