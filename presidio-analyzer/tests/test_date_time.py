from analyzer import matcher, common_pb2
from tests import *
import logging
import os


fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.DATE_TIME)
types = [fieldType]


def test_date_time_simple():
    name = 'May 1st'
    results = match.analyze_text(name + " is the workers holiday", types)
    assert results[0].text == name
