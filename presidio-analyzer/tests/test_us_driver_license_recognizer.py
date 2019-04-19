from unittest import TestCase
import os
from assertions import assert_result, assert_result_within_score_range
from analyzer.predefined_recognizers import UsLicenseRecognizer

us_license_recognizer = UsLicenseRecognizer()
entities = ["US_DRIVER_LICENSE"]


class TestUsLicenseRecognizer(TestCase):

    def test_valid_us_driver_license_weak_WA(self):
        num1 = 'AA1B2**9ABA7'
        num2 = 'A*1234AB*CD9'
        results = us_license_recognizer.analyze(
            '{} {}'.format(num1, num2), entities)

        assert len(results) == 2
        assert_result_within_score_range(
            results[0], entities[0], 0, 12, 0.3, 0.4)
        assert_result_within_score_range(
            results[1], entities[0], 13, 25, 0.3, 0.4)

    def test_invalid_us_driver_license_weak_WA(self):
        num = '3A1B2**9ABA7'
        results = us_license_recognizer.analyze(num, entities)

        assert len(results) == 0

    # Driver License - Alphanumeric (weak) - 0.3
    # Regex:r'\b([A-Z][0-9]{3,6}|[A-Z][0-9]{5,9}|[A-Z][0-9]{6,8}|[A-Z][0-9]{4,8}|[A-Z][0-9]{9,11}|[A-Z]{1,2}[0-9]{5,
    # 6}|H[0-9]{8}|V[0-9]{6}|X[0-9]{8}|A-Z]{2}[0-9]{2,5}|[A-Z]{2}[0-9]{3,7}|[0-9]{2}[A-Z]{3}[0-9]{5,6}|[A-Z][0-9]{13,
    # 14}|[A-Z][0-9]{18}|[A-Z][0-9]{6}R|[A-Z][0-9]{9}|[A-Z][0-9]{1,12}|[0-9]{9}[A-Z]|[A-Z]{2}[0-9]{6}[A-Z]|[0-9]{8}[
    # A-Z]{2}|[0-9]{3}[A-Z]{2}[0-9]{4}|[A-Z][0-9][A-Z][0-9][A-Z]|[0-9]{7,8}[A-Z])\b'

    def test_valid_us_driver_license_weak_alphanumeric(self):
        num = 'H12234567'
        results = us_license_recognizer.analyze(num, entities)

        assert len(results) == 1
        assert 0.29 < results[0].score < 0.49

     # Task #603: Support keyphrases
    ''' This test fails, since 'license' is a match and driver is a context.
        It should be fixed after adding support in keyphrase instead of keywords (context)
    def test_invalid_us_driver_license(self):
        num = 'C12T345672'
        results = us_license_recognizer.analyze('my driver license is ' + num, entities)
    
        assert len(results) == 0
    '''

    def test_invalid_us_driver_license(self):
        num = 'C12T345672'
        results = us_license_recognizer.analyze(num, entities)

        assert len(results) == 0

    # Driver License - Digits (very weak) - 0.05
    # Regex: r'\b([0-9]{1,9}|[0-9]{4,10}|[0-9]{6,10}|[0-9]{1,12}|[0-9]{12,14}|[0-9]{16})\b'

    def test_valid_us_driver_license_very_weak_digits(self):
        num = '123456789 1234567890 12345679012 123456790123 1234567901234'
        results = us_license_recognizer.analyze(num, entities)

        assert len(results) == 5
        for result in results:
            assert 0 < result.score < 0.02

    def test_load_from_file(self):
        path = os.path.dirname(__file__) + '/data/demo.txt'
        text_file = open(path, 'r')
        text = text_file.read()
        results = us_license_recognizer.analyze(text, entities)

        assert len(results) == 23

    # Driver License - Letters (very weak) - 0.00
    # Regex: r'\b([A-Z]{7,9}\b'

    def test_valid_us_driver_license_very_weak_letters(self):
        num = 'ABCDEFG ABCDEFGH ABCDEFGHI'
        results = us_license_recognizer.analyze(num, entities)

        assert len(results) == 0

     # Task #603: Support keyphrases
    ''' This test fails, since 'license' is a match and driver is a context.
        It should be fixed after adding support in keyphrase instead of keywords (context)
    def test_valid_us_driver_license_very_weak_letters_exact_context(self):
        num = 'ABCDEFG'
        context = 'my driver license: '
        results = us_license_recognizer.analyze(context + num, entities)
    
        assert len(results) == 1
        assert results[0].text == num
        assert results[0].score > 0.55 and results[0].score < 0.91
    '''

    def test_invalid_us_driver_license_very_weak_letters(self):
        num = 'ABCD ABCDEFGHIJ'
        results = us_license_recognizer.analyze(num, entities)

        assert len(results) == 0
