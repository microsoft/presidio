from analyzer import matcher, common_pb2
from tests import *
import os

# https://www.datatrans.ch/showcase/test-cc-numbers
# https://www.freeformatter.com/credit-card-number-generator-validator.html

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.CREDIT_CARD)
types = [fieldType]


def test_valid_credit_cards():
    number1 = '4012888888881881'
    number2 = '4012-8888-8888-1881'
    number3 = '4012 8888 8888 1881'
    results = match.analyze_text(
        '{} {} {}'.format(
            number1,
            number2,
            number3),
        types)

    assert len(results) == 3
    assert results[0].text == number1
    assert results[0].probability == 1.0
    assert results[1].text == number2
    assert results[1].probability == 1.0
    assert results[2].text == number3
    assert results[2].probability == 1.0


def test_valid_credit_cards_with_lemmatized_context():
    number1 = '4012888888881881'
    number2 = '4012-8888-8888-1881'
    number3 = '4012 8888 8888 1881'
    context = 'my credit cards are:'
    results = match.analyze_text(
        '{}{} {} {}'.format(
            context,
            number1,
            number2,
            number3),
        types)

    assert len(results) == 3
    assert results[0].text == number1
    assert results[0].probability == 1.0
    assert results[1].text == number2
    assert results[1].probability == 1.0
    assert results[2].text == number3
    assert results[2].probability == 1.0


def test_valid_airplus_credit_card():
    number = '122000000000003'
    results = match.analyze_text(number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_valid_airplus_credit_card_with_extact_context():
    number = '122000000000003'
    context = 'my credit card:'
    results = match.analyze_text(context + number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_valid_amex_credit_card():
    number = '371449635398431'
    results = match.analyze_text(number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_valid_cartebleue_credit_card():
    number = '5555555555554444'
    results = match.analyze_text(number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_valid_dankort_credit_card():
    number = '5019717010103742'
    results = match.analyze_text(number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_valid_diners_credit_card():
    number = '30569309025904'
    results = match.analyze_text(number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_valid_discover_credit_card():
    number = '6011000400000000'
    results = match.analyze_text(number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_valid_jcb_credit_card():
    number = '3528000700000000'
    results = match.analyze_text(number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_valid_maestro_credit_card():
    number = '6759649826438453'
    results = match.analyze_text(number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_valid_mastercard_credit_card():
    number = '5555555555554444'
    results = match.analyze_text(number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_valid_visa_credit_card():
    number = '4111111111111111'
    results = match.analyze_text(number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_valid_visa_debit_credit_card():
    number = '4111111111111111'
    results = match.analyze_text(number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0
    

def test_valid_visa_electron_credit_card():
    number = '4917300800000000'
    results = match.analyze_text(number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_valid_visa_purchasing_credit_card():
    number = '4484070000000000'
    results = match.analyze_text(number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].probability == 1.0


def test_invalid_credit_card():
    number = '4012-8888-8888-1882'
    results = match.analyze_text('my credit card number is ' + number, types)

    assert len(results) == 0


def test_invalid_diners_card():
    number = '36168002586008'
    results = match.analyze_text('my credit card number is ' + number, types)

    assert len(results) == 0
