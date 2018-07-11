from analyzer import matcher
from analyzer import common_pb2

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.US_DRIVER_LICENSE)
types = [fieldType]


def test_valid_us_driver_license():
    match = matcher.Matcher()
    num = 'H12234567'
    results = match.analyze_text('my driver license is ' + num, types)
    assert len(results) == 1


def test_invalid_us_driver_license():
    match = matcher.Matcher()
    num = 'C12T345672'
    results = match.analyze_text('my driver license is ' + num, types)
    assert len(results) == 0
