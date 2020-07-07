from unittest import TestCase

from assertions import assert_result
from presidio_analyzer.predefined_recognizers import INDLicenseRecognizer

ind_license_recognizer = INDLicenseRecognizer()
entities = ["license"]


class TestINDLicenseRecognizer(TestCase):

    def test_valid_license(self):
        num = 'KA32 20191234567'
        results = ind_license_recognizer.analyze(num, entities)
        assert len(results) == 1

    def test_invalid_license(self):
        num = 'KA32 56984569874'
        results = ind_license_recognizer.analyze(num, entities)
        assert len(results) == 0