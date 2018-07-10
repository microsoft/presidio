from analyzer import matcher
from analyzer import common_pb2

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.CRYPTO)
types = [fieldType]

# Generate random address https://www.bitaddress.org/


def test_valid_btc():
    match = matcher.Matcher()
    wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ'
    results = match.analyze_text('my wallet address is ' + wallet, types)
    assert len(results) == 1


def test_invalid_btc():
    match = matcher.Matcher()
    wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ2'
    results = match.analyze_text('my wallet address is ' + wallet, types)
    assert len(results) == 0
