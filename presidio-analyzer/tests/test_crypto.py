from analyzer import matcher, common_pb2
from tests import *

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.CRYPTO)
types = [fieldType]

# Generate random address https://www.bitaddress.org/


def test_valid_btc():
    wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ'
    results = match.analyze_text(wallet, types)

    assert len(results) == 1
    assert results[0].text == wallet
    assert results[0].score == 1


def test_valid_btc_with_exact_context():
    wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ'
    context = 'my wallet address is: '
    results = match.analyze_text(context + wallet, types)

    assert len(results) == 1
    assert results[0].text == wallet
    assert results[0].score == 1


def test_invalid_btc():
    wallet = '16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ2'
    results = match.analyze_text('my wallet address is ' + wallet, types)

    assert len(results) == 0
