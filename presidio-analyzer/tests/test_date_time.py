from analyzer import matcher
from analyzer import common_pb2
import logging

import os

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.DATE_TIME)
types = [fieldType]


def test_date_time_simple():
    match = matcher.Matcher()
    name = 'May 1st'
    results = match.analyze_text(name + " is the workers holiday", types)
    assert results[0].text == name
