from analyzer import matcher, common_pb2
from tests import *
import os

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.US_DRIVER_LICENSE)
types = [fieldType]


def test_valid_us_driver_license():
    num = 'H12234567'
    results = match.analyze_text(num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].probability > 0.29 and results[0].probability < 0.31


def test_valid_us_driver_license_with_exact_context():
    num = 'H12234567'
    context = 'my driver license is '
    results = match.analyze_text(context + num, types)

    assert len(results) == 1
    assert results[0].text == num
    #assert results[0].probability > 0.45 and results[0].probability < 0.71


def test_invalid_us_driver_license():
    num = 'C12T345672'
    results = match.analyze_text('my driver license is ' + num, types)

    assert len(results) == 0


'''
def test_load_from_file():
    path = os.path.dirname(__file__) + '/data/demo.txt'
    text_file = open(path, 'r')
    text = text_file.read()
    results = match.analyze_text(text, types)
    assert len(results) == 1
'''
