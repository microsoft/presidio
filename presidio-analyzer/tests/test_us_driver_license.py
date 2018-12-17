from analyzer import matcher, common_pb2
from tests import *
import os

fieldType = common_pb2.FieldTypes()
fieldType.name = common_pb2.FieldTypesEnum.Name(common_pb2.US_DRIVER_LICENSE)
types = [fieldType]

# Driver License - WA (weak) - 0.3
# Regex: '\b([A-Z][A-Z0-9*]{11})\b'


def test_valid_us_driver_license_weak_WA():
    num1 = 'AA1B2**9ABA7'
    num2 = 'A*1234AB*CD9'
    results = match.analyze_text('{} {}'.format(num1, num2), types)

    assert len(results) == 2
    assert results[0].text == num1
    assert results[0].score > 0.29 and results[0].score < 0.41
    assert results[1].text == num2
    assert results[1].score > 0.29 and results[1].score < 0.41


def test_valid_us_driver_license_weak_WA_exact_Context():
    num = 'AA1B2**9ABA7'
    context = 'my driver license number: '
    results = match.analyze_text(context + num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].score > 0.55 and results[0].score < 0.91


def test_invalid_us_driver_license_weak_WA():
    num = '3A1B2**9ABA7'
    results = match.analyze_text(num, types)

    assert len(results) == 0


# Driver License - Alphanumeric (weak) - 0.3
# Regex:r'\b([A-Z][0-9]{3,6}|[A-Z][0-9]{5,9}|[A-Z][0-9]{6,8}|[A-Z][0-9]{4,8}|[A-Z][0-9]{9,11}|[A-Z]{1,2}[0-9]{5,6}|H[0-9]{8}|V[0-9]{6}|X[0-9]{8}|A-Z]{2}[0-9]{2,5}|[A-Z]{2}[0-9]{3,7}|[0-9]{2}[A-Z]{3}[0-9]{5,6}|[A-Z][0-9]{13,14}|[A-Z][0-9]{18}|[A-Z][0-9]{6}R|[A-Z][0-9]{9}|[A-Z][0-9]{1,12}|[0-9]{9}[A-Z]|[A-Z]{2}[0-9]{6}[A-Z]|[0-9]{8}[A-Z]{2}|[0-9]{3}[A-Z]{2}[0-9]{4}|[A-Z][0-9][A-Z][0-9][A-Z]|[0-9]{7,8}[A-Z])\b'


def test_valid_us_driver_license_weak_lphanumeric():
    num = 'H12234567'
    results = match.analyze_text(num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].score > 0.29 and results[0].score < 0.49


def test_valid_us_driver_license_weak_lphanumeric_exact_context():
    num = 'H12234567'
    context = 'my driver license is '
    results = match.analyze_text(context + num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].score > 0.59 and results[0].score < 0.91


''' This test fails, since 'license' is a match and driver is a context.
    It should be fixed after adding support in keyphrase instead of keywords (context)
def test_invalid_us_driver_license():
    num = 'C12T345672'
    results = match.analyze_text('my driver license is ' + num, types)

    assert len(results) == 0
'''


def test_invalid_us_driver_license():
    num = 'C12T345672'
    results = match.analyze_text(num, types)

    assert len(results) == 0


# Driver License - Digits (very weak) - 0.05
# Regex: r'\b([0-9]{1,9}|[0-9]{4,10}|[0-9]{6,10}|[0-9]{1,12}|[0-9]{12,14}|[0-9]{16})\b'


def test_valid_us_driver_license_very_weak_digits():
    num = '123456789 1234567890 12345679012 123456790123 1234567901234'
    results = match.analyze_text(num, types)

    assert len(results) == 5
    for result in results:
        assert result.score > 0 and result.score < 0.1


def test_valid_us_driver_license_very_weak_digits_exact_context():
    num = '1234567901234'
    context = 'my driver license is: '
    results = match.analyze_text(context + num, types)

    assert len(results) == 1
    assert results[0].text == num
    assert results[0].score > 0.55 and results[0].score < 0.91


# Driver License - Letters (very weak) - 0.00
# Regex: r'\b([A-Z]{7,9}\b'


def test_valid_us_driver_license_very_weak_letters():
    num = 'ABCDEFG ABCDEFGH ABCDEFGHI'
    results = match.analyze_text(num, types)

    assert len(results) == 0


''' This test fails, since 'license' is a match and driver is a context.
    It should be fixed after adding support in keyphrase instead of keywords (context)
def test_valid_us_driver_license_very_weak_letters_exact_context():
    num = 'ABCDEFG'
    context = 'my driver license: '
    results = match.analyze_text(context + num, types)
    
    assert len(results) == 1
    assert results[0].text == num
    assert results[0].score > 0.55 and results[0].score < 0.91
'''


def test_invalid_us_driver_license_very_weak_letters():
    num = 'ABCD ABCDEFGHIJ'
    results = match.analyze_text(num, types)

    assert len(results) == 0


def test_load_from_file():
    path = os.path.dirname(__file__) + '/data/demo.txt'
    text_file = open(path, 'r')
    text = text_file.read()
    results = match.analyze_text(text, types)
    assert len(results) == 1
