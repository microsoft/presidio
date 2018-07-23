from analyzer import matcher
from analyzer import common_pb2
import logging
import os


fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.IBAN_CODE)
types = [fieldType]

match = matcher.Matcher()

def test_valid_iban():
    number = 'IL150120690000003111111'
    results = match.analyze_text('my iban number is ' + number, types)
    assert len(results) == 1


def test_invalid_iban():
    number = 'IL150120690000003111141'
    results = match.analyze_text('my iban number is ' + number, types)
    assert len(results) == 0
