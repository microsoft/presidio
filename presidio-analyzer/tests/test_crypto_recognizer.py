from unittest import TestCase

from analyzer.predefined_recognizers import CryptoRecognizer

crypto_recognizer = CryptoRecognizer()
entities = ["CRYPTO"]


# Generate random address https://www.bitaddress.org/

class TestCreditCardRecognizer(TestCase):

    def test_valid_btc(self):
        wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ'
        results = crypto_recognizer.analyze(wallet, entities)

        assert len(results) == 1
        assert results[0].score == 1
        assert results[0].entity_type == entities[0]
        assert results[0].start == 0
        assert results[0].end == 34

    def test_valid_btc_with_exact_context(self):
        wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ'
        context = 'my wallet address is: '
        results = crypto_recognizer.analyze(context + wallet, entities)

        assert len(results) == 1
        assert results[0].score == 1
        assert results[0].entity_type == entities[0]
        assert results[0].start == 22
        assert results[0].end == 56

    def test_invalid_btc(self):
        wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ2'
        results = crypto_recognizer.analyze('my wallet address is ' + wallet, entities)

        assert len(results) == 0
