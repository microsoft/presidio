from analyzer import matcher
from analyzer import common_pb2
import os

# https://www.datatrans.ch/showcase/test-cc-numbers

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.CREDIT_CARD)
types = [fieldType]


def test_valid_credit_card():
    match = matcher.Matcher()
    number = '4012888888881881 4012-8888-8888-1881 4012 8888 8888 1881'
    results = match.analyze_text('my credit card number is ' + number, types)
    assert len(results) == 3


def test_invalid_credit_card():
    match = matcher.Matcher()
    number = '4012-8888-8888-1882'
    results = match.analyze_text('my credit card number is ' + number, types)
    assert len(results) == 0
