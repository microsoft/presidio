from analyzer import matcher, common_pb2
from tests import *

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.US_ITIN)
types = [fieldType]


def test_valid_us_itin_very_weak_match():
    num1 = '911-701234'
    num2 = '91170-1234'
    results = match.analyze_text('{} {}'.format(num1, num2), types)

    assert len(results) == 2
    assert results[0].text == num1
    assert results[0].score > 0 and results[0].score < 0.31
    assert results[1].text == num2
    assert results[1].score > 0 and results[0].score < 0.31


def test_valid_us_itin_weak_match():
    num = '911701234'
    results = match.analyze_text(num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].score > 0.29 and results[0].score < 0.41


def test_valid_us_itin_medium_match():
    num = '911-70-1234'
    results = match.analyze_text(num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].score > 0.49 and results[0].score < 0.6


def test_valid_us_itin_very_weak_match_exact_context():
    num1 = '911-701234'
    num2 = '91170-1234'
    context = "my taxpayer id is"
    results = match.analyze_text('{} {} {}'.format(context, num1, num2), types)

    assert len(results) == 2
    assert results[0].text == num1
    assert results[0].score > 0.59 and results[0].score < 0.7
    assert results[1].text == num2
    assert results[1].score > 0.50 and results[0].score < 0.7


def test_valid_us_itin_weak_match_exact_context():
    num = '911701234'
    context = "my itin:"
    results = match.analyze_text('{} {}'.format(context, num), types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].score > 0.5 and results[0].score < 0.65


def test_valid_us_itin_medium_match_exact_context():
    num = '911-70-1234'
    context = "my itin is"
    results = match.analyze_text('{} {}'.format(context, num), types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].score > 0.6 and results[0].score < 0.9


def test_invalid_us_itin():
    num = '911-89-1234'
    results = match.analyze_text(num, types)

    assert len(results) == 0


def test_invalid_us_itin_exact_context():
    num = '911-89-1234'
    context = "my taxpayer id"
    results = match.analyze_text('{} {}'.format(context, num), types)

    assert len(results) == 0
