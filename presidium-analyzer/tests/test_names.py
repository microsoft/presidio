from analyzer import matcher
from analyzer import common_pb2

import logging

import os


fieldType = common_pb2.FieldTypes()
fieldType.name = "PERSON"
types = [fieldType]


def test_person_name_simple():
    match = matcher.Matcher()
    name = 'John Oliver'
    results = match.analyze_text(name + " is the funniest comedian", types)

    assert results[0].text == name
