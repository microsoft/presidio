from analyzer import matcher
from analyzer import common_pb2
import logging
import os

# https://www.datatrans.ch/showcase/test-cc-numbers

fieldType = common_pb2.FieldTypes()
fieldType.name = "IBAN_CODE"
types = [fieldType]


def test_valid_iban():
    match = matcher.Matcher()

    number = 'IL150120690000003111111'
    results = match.analyze_text('my credit card number is ' + number, types)

    assert len(results) == 1


def test_invalid_iban():
    match = matcher.Matcher()

    number = 'IL150120690000003111141'
    results = match.analyze_text('my credit card number is ' + number, types)

    assert len(results) == 0
