from analyzer import matcher
from analyzer import common_pb2

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.US_SSN)
types = [fieldType]


def test_valid_us_ssn():
    match = matcher.Matcher()
    num = '078-05-1120'
    results = match.analyze_text('my ssn is ' + num, types)
    assert len(results) == 1


def test_invalid_us_itin():
    match = matcher.Matcher()
    num = '078-05-11201'
    results = match.analyze_text('my ssn is ' + num, types)
    assert len(results) == 0
