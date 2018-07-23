from analyzer import matcher
from analyzer import common_pb2

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.US_ITIN)
types = [fieldType]

match = matcher.Matcher()

def test_valid_us_itin():
    num = '912-80-3456'
    results = match.analyze_text('my itin is ' + num, types)
    assert len(results) == 1


def test_invalid_us_itin():
    num = '912-30-3456'
    results = match.analyze_text('my itin is ' + num, types)
    assert len(results) == 0
