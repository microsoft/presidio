from unittest import TestCase

from tests import assert_result
from analyzer.predefined_recognizers import CryptoRecognizer
from analyzer.entity_recognizer import EntityRecognizer

crypto_recognizer = CryptoRecognizer()
entities = ["CRYPTO"]


# Generate random address https://www.bitaddress.org/

class TestCreditCardRecognizer(TestCase):

    def test_valid_btc(self):
        wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ'
        results = crypto_recognizer.analyze(wallet, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 34, EntityRecognizer.MAX_SCORE)

    def test_valid_btc_with_exact_context(self):
        wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ'
        results = crypto_recognizer.analyze('my wallet address is: ' + wallet, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 22, 56, EntityRecognizer.MAX_SCORE)

    def test_invalid_btc(self):
        wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ2'
        results = crypto_recognizer.analyze('my wallet address is ' + wallet, entities)

        assert len(results) == 0

    def test_invalid_btc_chars(self):
        wallet = '34e7b5e1a0aa1d6f3d862b52a289cdb7'
        results = crypto_recognizer.analyze('my wallet address is ' + wallet, entities)

        assert len(results) == 0