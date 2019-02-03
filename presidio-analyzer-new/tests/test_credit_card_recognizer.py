# https://www.datatrans.ch/showcase/test-cc-numbers
# https://www.freeformatter.com/credit-card-number-generator-validator.html
from analyzer.predefined_recognizers.credit_card_recognizer import CreditCardRecognizer


credit_card_recognizer = CreditCardRecognizer()
entities = ["CREDIT_CARD"]


def test_valid_credit_cards():
    # init
    number1 = '4012888888881881'
    number2 = '4012-8888-8888-1881'
    number3 = '4012 8888 8888 1881'

    results = credit_card_recognizer.analyze_all('{} {} {}'.format(number1, number2, number3), entities)

    assert len(results) == 3
    assert results[0].entity_type == "CREDIT_CARD"
    assert results[0].score == 1.0
    assert results[1].score == 1.0
    assert results[2].score == 1.0


def test_valid_airplus_credit_card():
    number = '122000000000003'
    results = credit_card_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_valid_airplus_credit_card_with_extact_context():
    number = '122000000000003'
    context = 'my credit card:'
    results = credit_card_recognizer.analyze_all(context + number, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_valid_amex_credit_card():
    number = '371449635398431'
    results = credit_card_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_valid_cartebleue_credit_card():
    number = '5555555555554444'
    results = credit_card_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_valid_dankort_credit_card():
    number = '5019717010103742'
    results = credit_card_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_valid_diners_credit_card():
    number = '30569309025904'
    results = credit_card_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_valid_discover_credit_card():
    number = '6011000400000000'
    results = credit_card_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_valid_jcb_credit_card():
    number = '3528000700000000'
    results = credit_card_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_valid_maestro_credit_card():
    number = '6759649826438453'
    results = credit_card_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_valid_mastercard_credit_card():
    number = '5555555555554444'
    results = credit_card_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_valid_visa_credit_card():
    number = '4111111111111111'
    results = credit_card_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_valid_visa_debit_credit_card():
    number = '4111111111111111'
    results = credit_card_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_valid_visa_electron_credit_card():
    number = '4917300800000000'
    results = credit_card_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_valid_visa_purchasing_credit_card():
    number = '4484070000000000'
    results = credit_card_recognizer.analyze_all(number, entities)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_invalid_credit_card():
    number = '4012-8888-8888-1882'
    results = credit_card_recognizer.analyze_all('my credit card number is ' + number, entities)

    assert len(results) == 0


def test_invalid_diners_card():
    number = '36168002586008'
    results = credit_card_recognizer.analyze_all('my credit card number is ' + number, entities)

    assert len(results) == 0
