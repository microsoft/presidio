from unittest import TestCase

from assertions import assert_result
from analyzer.predefined_recognizers import UsBankRecognizer

us_bank_recognizer = UsBankRecognizer()
entities = ["US_BANK_NUMBER"]


class TestUsBankRecognizer(TestCase):

    def test_us_bank_account_invalid_number(self):
        num = '1234567'
        results = us_bank_recognizer.analyze(num, entities)

        assert len(results) == 0

    def test_us_bank_account_no_context(self):
        num = '945456787654'
        results = us_bank_recognizer.analyze(num, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 12, 0.05)
