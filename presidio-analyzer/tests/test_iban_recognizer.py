from unittest import TestCase

from assertions import assert_result
from analyzer.predefined_recognizers import IbanRecognizer

iban_recognizer = IbanRecognizer()
entities = ["IBAN_CODE"]


class TestIbanRecognizer(TestCase):

    def test_valid_iban(self):
        number = 'IL150120690000003111111'
        results = iban_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 23, 1.0)

    def test_invalid_iban(self):
        number = 'IL150120690000003111141'
        results = iban_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 23, 0)

    def test_invalid_iban_with_exact_context_does_not_change_Score(self):
        number = 'IL150120690000003111141'
        context = 'my iban number is '
        results = iban_recognizer.analyze(context + number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 18, 41, 0)
