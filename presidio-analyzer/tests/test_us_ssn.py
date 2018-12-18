from analyzer import matcher, common_pb2
from tests import *

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.US_SSN)
types = [fieldType]


def test_valid_us_ssn_very_weak_match():
    num1 = '078-051120'
    num2 = '07805-1120'
    results = match.analyze_text('{} {}'.format(num1, num2), types)

    assert len(results) == 2
    assert results[0].text == num1
    assert results[0].score > 0.01 and results[0].score < 0.31
    assert results[1].text == num2
    assert results[1].score > 0.01 and results[0].score < 0.31


def test_valid_us_ssn_weak_match():
    num = '078051120'
    results = match.analyze_text(num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].score > 0.29 and results[0].score < 0.41


def test_valid_us_ssn_medium_match():
    num = '078-05-1120'
    results = match.analyze_text(num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].score > 0.49 and results[0].score < 0.6


def test_valid_us_ssn_very_weak_match_exact_context():
    num1 = '078-051120'
    num2 = '07805-1120'
    context = "my ssn is "
    results = match.analyze_text('{} {} {}'.format(context, num1, num2), types)

    assert len(results) == 2
    assert results[0].text == num1
    assert results[0].score > 0.59 and results[0].score < 0.7
    assert results[1].text == num2
    assert results[1].score > 0.59 and results[0].score < 0.7


def test_valid_us_ssn_weak_match_exact_context():
    num = '078051120'
    context = "my social security number is "
    results = match.analyze_text(context + num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].score > 0.5 and results[0].score < 0.65


def test_valid_us_ssn_medium_match_exact_context():
    num = '078-05-1120'
    context = "my social security number is "
    results = match.analyze_text(context + num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].score > 0.6 and results[0].score < 0.9


def test_invalid_us_ssn():
    num = '078-05-11201'
    results = match.analyze_text(num, types)

    assert len(results) == 0


def test_invalid_us_ssn_exact_context():
    num = '078-05-11201'
    context = "my ssn is "
    results = match.analyze_text(context + num, types)

    assert len(results) == 0
