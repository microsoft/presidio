from unittest import TestCase

from assertions import assert_result
from analyzer.predefined_recognizers import SgFinRecognizer

sg_fin_recognizer = SgFinRecognizer()
entities = ["FIN","NRIC"]


class TestSgFinRecognizer(TestCase):

    def test_valid_fin_with_allchars(self):
        num = 'G1122144L'
        results = sg_fin_recognizer.analyze(num, entities)
        assert len(results) == 2

    def test_invalid_fin(self):
        num = 'PA12348L'
        results = sg_fin_recognizer.analyze(num, entities)
        assert len(results) == 0
