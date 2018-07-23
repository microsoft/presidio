from analyzer import matcher
from analyzer import common_pb2

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.US_BANK_NUMBER)
types = [fieldType]

match = matcher.Matcher()

def test_valid_us_bank_number():
    num = '945456787654'
    results = match.analyze_text('my account number is ' + num, types)
    assert len(results) == 1


def test_invalid_us_bank_number():
    num = '123456'
    results = match.analyze_text('my account number is ' + num, types)
    assert len(results) == 0
