from analyzer import matcher
from analyzer import common_pb2
import logging

import os

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.DATE_TIME)
types = [fieldType]

match = matcher.Matcher()

def test_date_time_simple():
    name = 'May 1st'
    results = match.analyze_text(name + " is the workers holiday", types)
    assert results[0].text == name
