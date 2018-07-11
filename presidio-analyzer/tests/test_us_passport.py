from analyzer import matcher
from analyzer import common_pb2

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.US_PASSPORT)
types = [fieldType]


def test_valid_us_passport():
    match = matcher.Matcher()
    num = '912803456'
    results = match.analyze_text('my passport number is ' + num, types)
    assert len(results) == 1


def test_invalid_us_passport():
    match = matcher.Matcher()
    num = '9345617787'
    results = match.analyze_text('my passport number is ' + num, types)
    assert len(results) == 0
