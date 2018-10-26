from analyzer import matcher, common_pb2
from tests import *

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.UK_NHS)
types = [fieldType]


def test_valid_uk_nhs():
    num = '401-023-2137'
    results = match.analyze_text(num, types)
    assert len(results) == 1
    assert results[0].text == num

    num = '221 395 1837'
    results = match.analyze_text(num, types)
    assert len(results) == 1
    assert results[0].text == num

    num = '0032698674'
    results = match.analyze_text(num, types)
    assert len(results) == 1
    assert results[0].text == num


def test_invalid_uk_nhs():
    num = '401-023-2138'
    results = match.analyze_text(num, types)

    assert len(results) == 0