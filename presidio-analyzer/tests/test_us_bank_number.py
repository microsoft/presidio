from analyzer import matcher, common_pb2
from tests import *

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.US_BANK_NUMBER)
types = [fieldType]


def test_us_bank_account_invalid_number():
    num = '1234567'
    results = match.analyze_text(num, types)

    assert len(results) == 0


def test_us_bank_account_no_context():
    num = '945456787654'
    results = match.analyze_text(num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].probability > 0 and results[0].probability < 0.1


def test_us_passport_with_exact_context():
    num = '912803456'
    context = 'my banck account number is '
    results = match.analyze_text(context + num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].probability > 0.49 and results[0].probability < 0.61


def test_us_passport_with_lemmatized_context():
    num = '912803456'
    context = 'my banking account number is '
    results = match.analyze_text(context + num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].probability > 0.49 and results[0].probability < 0.61
