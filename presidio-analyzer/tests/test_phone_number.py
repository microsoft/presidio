from analyzer import matcher
from analyzer import common_pb2

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.PHONE_NUMBER)
types = [fieldType]


def test_phone_number_simple():
    match = matcher.Matcher()
    number = '052-5552606'
    results = match.analyze_text('my phone number is ' + number, types)
    assert results[0].text == number
