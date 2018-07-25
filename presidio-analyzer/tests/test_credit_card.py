from analyzer import matcher, common_pb2
from tests import *
import os

# https://www.datatrans.ch/showcase/test-cc-numbers

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.CREDIT_CARD)
types = [fieldType]

def test_valid_credit_card():
    number = '4012888888881881 4012-8888-8888-1881 4012 8888 8888 1881'
    results = match.analyze_text('my credit card number is ' + number, types)
    assert len(results) == 3


def test_valid_airplus_credit_card():
    number = '122000000000003'
    results = match.analyze_text(number, types)
    assert len(results) == 1


def test_valid_amex_credit_card():
    number = '371449635398431'
    results = match.analyze_text(number, types)
    assert len(results) == 1


def test_valid_cartebleue_credit_card():
    number = '5555555555554444'
    results = match.analyze_text(number, types)
    assert len(results) == 1


def test_valid_dankort_credit_card():
    number = '5019717010103742'
    results = match.analyze_text(number, types)
    assert len(results) == 1


def test_valid_diners_credit_card():
    number = '30569309025904'
    results = match.analyze_text(number, types)
    assert len(results) == 1


def test_valid_discover_credit_card():
    number = '6011000400000000'
    results = match.analyze_text(number, types)
    assert len(results) == 1


def test_valid_jcb_credit_card():
    number = '3528000700000000'
    results = match.analyze_text(number, types)
    assert len(results) == 1


def test_valid_maestro_credit_card():
    number = '6759649826438453'
    results = match.analyze_text(number, types)
    assert len(results) == 1


def test_valid_mastercard_credit_card():
    number = '5555555555554444'
    results = match.analyze_text(number, types)
    assert len(results) == 1


def test_valid_visa_credit_card():
    number = '4111111111111111'
    results = match.analyze_text(number, types)
    assert len(results) == 1


def test_valid_visa_debit_credit_card():
    number = '4111111111111111'
    results = match.analyze_text(number, types)
    assert len(results) == 1


def test_valid_visa_electron_credit_card():
    number = '4917300800000000'
    results = match.analyze_text(number, types)
    assert len(results) == 1


def test_valid_visa_purchasing_credit_card():
    number = '4484070000000000'
    results = match.analyze_text(number, types)
    assert len(results) == 1


def test_invalid_credit_card():
    number = '4012-8888-8888-1882'
    results = match.analyze_text('my credit card number is ' + number, types)
    assert len(results) == 0
