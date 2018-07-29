from analyzer import matcher, common_pb2
from tests import *

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.US_PASSPORT)
types = [fieldType]

def test_valid_us_passport_no_context():
    num = '912803456'
    results = match.analyze_text(num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].probability > 0 and results[0].probability < 0.1

def test_valid_us_passport_with_exact_context():
    num = '912803456'
    context = 'my passport number is '
    results = match.analyze_text(context + num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].probability > 0.49 and results[0].probability < 0.7

