from analyzer import matcher, common_pb2
from tests import *
import logging
import os

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.IBAN_CODE)
types = [fieldType]


def test_valid_iban():
    number = 'IL150120690000003111111'
    results = match.analyze_text(number, types)

    assert len(results) == 1
    assert results[0].text == number
    assert results[0].score == 1


def test_invalid_iban():
    number = 'IL150120690000003111141'
    results = match.analyze_text(number, types)

    assert len(results) == 0


# Context should not change the result if the checksum fails
def test_invalid_iban_with_exact_context():
    number = 'IL150120690000003111141'
    context = 'my iban number is '
    results = match.analyze_text(context + number, types)

    assert len(results) == 0
