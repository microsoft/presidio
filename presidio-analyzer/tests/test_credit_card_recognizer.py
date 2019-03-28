# https://www.datatrans.ch/showcase/test-cc-numbers
# https://www.freeformatter.com/credit-card-number-generator-validator.html
from unittest import TestCase

from assertions import assert_result
from analyzer.predefined_recognizers import CreditCardRecognizer
from analyzer.entity_recognizer import EntityRecognizer


entities = ["CREDIT_CARD"]
credit_card_recognizer = CreditCardRecognizer()

class TestCreditCardRecognizer(TestCase):

    def test_valid_credit_cards(self):
        # init
        number1 = '4012888888881881'
        number2 = '4012-8888-8888-1881'
        number3 = '4012 8888 8888 1881'

        results = credit_card_recognizer.analyze('{} {} {}'.format(number1, number2, number3), entities)

        assert len(results) == 3
        assert_result(results[0], entities[0], 0, 16, EntityRecognizer.MAX_SCORE)
        assert_result(results[1], entities[0], 17, 36, EntityRecognizer.MAX_SCORE)
        assert_result(results[2], entities[0], 37, 56, EntityRecognizer.MAX_SCORE)

    def test_valid_airplus_credit_card(self):
        number = '122000000000003'
        results = credit_card_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 15, EntityRecognizer.MAX_SCORE)

    def test_valid_airplus_credit_card_with_extact_context(self):
        number = '122000000000003'
        context = 'my credit card: '
        results = credit_card_recognizer.analyze(context + number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 16, 31, EntityRecognizer.MAX_SCORE)

    def test_valid_amex_credit_card(self):
        number = '371449635398431'
        results = credit_card_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 15, EntityRecognizer.MAX_SCORE)

    def test_valid_cartebleue_credit_card(self):
        number = '5555555555554444'
        results = credit_card_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 16, EntityRecognizer.MAX_SCORE)

    def test_valid_dankort_credit_card(self):
        number = '5019717010103742'
        results = credit_card_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 16, EntityRecognizer.MAX_SCORE)

    def test_valid_diners_credit_card(self):
        number = '30569309025904'
        results = credit_card_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 14, EntityRecognizer.MAX_SCORE)

    def test_valid_discover_credit_card(self):
        number = '6011000400000000'
        results = credit_card_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 16, EntityRecognizer.MAX_SCORE)

    def test_valid_jcb_credit_card(self):
        number = '3528000700000000'
        results = credit_card_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 16, EntityRecognizer.MAX_SCORE)

    def test_valid_maestro_credit_card(self):
        number = '6759649826438453'
        results = credit_card_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 16, EntityRecognizer.MAX_SCORE)

    def test_valid_mastercard_credit_card(self):
        number = '5555555555554444'
        results = credit_card_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 16, EntityRecognizer.MAX_SCORE)

    def test_valid_visa_credit_card(self):
        number = '4111111111111111'
        results = credit_card_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 16, EntityRecognizer.MAX_SCORE)

    def test_valid_visa_debit_credit_card(self):
        number = '4111111111111111'
        results = credit_card_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 16, EntityRecognizer.MAX_SCORE)

    def test_valid_visa_electron_credit_card(self):
        number = '4917300800000000'
        results = credit_card_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert_result(results[0], entities[0], 0, 16, EntityRecognizer.MAX_SCORE)

    def test_valid_visa_purchasing_credit_card(self):
        number = '4484070000000000'
        results = credit_card_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert results[0].score == 1.0
        assert_result(results[0], entities[0], 0, 16, EntityRecognizer.MAX_SCORE)

    def test_invalid_credit_card_with_no_context(self):
        number = '4012-8888-8888-1882'
        results = credit_card_recognizer.analyze(number, entities)

        assert not results

    def test_invalid_credit_card_with_context(self):
        number = '4012-8888-8888-1882'
        results = credit_card_recognizer.analyze('my credit card number is ' + number, entities)

        assert not results

    def test_invalid_diners_card_with_no_context(self):
        number = '36168002586008'
        results = credit_card_recognizer.analyze(number, entities)

        assert not results
    
    def test_invalid_diners_card_with_context(self):
        number = '36168002586008'
        results = credit_card_recognizer.analyze('my credit card number is ' + number, entities)

        assert not results
