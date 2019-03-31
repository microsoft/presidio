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

    def test_us_passport_with_exact_context(self):
        num = '912803456'
        context = 'my bank account number is '
        results = us_bank_recognizer.analyze(context + num, entities)

        assert len(results) == 1
        assert 0.49 < results[0].score < 0.61

    def test_us_passport_with_exact_context_no_space(self):
        num = '912803456'
        context = 'my bank account number is:'
        results = us_bank_recognizer.analyze(context + num, entities)

        assert len(results) == 1
        assert 0.49 < results[0].score < 0.61

    def test_us_passport_with_lemma_context(self):
        num = '912803456'
        context = 'my banking account number is '
        results = us_bank_recognizer.analyze(context + num, entities)
        assert len(results) == 1
        assert 0.49 < results[0].score < 0.61
