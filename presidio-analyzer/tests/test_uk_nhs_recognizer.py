from unittest import TestCase

from analyzer.predefined_recognizers import NhsRecognizer

nhs_recognizer = NhsRecognizer()
entities = ["UK_NHS"]


class TestNhsRecognizer(TestCase):

    def test_valid_uk_nhs(self):
        num = '401-023-2137'
        results = nhs_recognizer.analyze(num, entities)
        assert len(results) == 1
        assert results[0].score == 1.0
        assert results[0].start == 0
        assert results[0].end == 12
        assert results[0].entity_type == entities[0]

        num = '221 395 1837'
        results = nhs_recognizer.analyze(num, entities)
        assert len(results) == 1
        assert results[0].score == 1.0
        assert results[0].start == 0
        assert results[0].end == 12
        assert results[0].entity_type == entities[0]

        num = '0032698674'
        results = nhs_recognizer.analyze(num, entities)
        assert len(results) == 1
        assert results[0].score == 1.0
        assert results[0].start == 0
        assert results[0].end == 10
        assert results[0].entity_type == entities[0]


    def test_invalid_uk_nhs(self):
        num = '401-023-2138'
        results = nhs_recognizer.analyze(num, entities)

        assert len(results) == 1
        assert results[0].score == 0
        assert results[0].start == 0
        assert results[0].end == 12
        assert results[0].entity_type == entities[0]
