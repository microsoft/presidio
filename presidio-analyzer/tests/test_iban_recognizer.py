from unittest import TestCase

from analyzer.predefined_recognizers import IbanRecognizer

iban_recognizer = IbanRecognizer()
entities = ["IBAN_CODE"]


class TestIbanRecognizer(TestCase):

    def test_valid_iban(self):
        number = 'IL150120690000003111111'
        results = iban_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert results[0].score == 1
        assert results[0].entity_type == entities[0]
        assert results[0].start == 0
        assert results[0].end == 23


    def test_invalid_iban(self):
        number = 'IL150120690000003111141'
        results = iban_recognizer.analyze(number, entities)

        assert len(results) == 1
        assert results[0].score == 0
        assert results[0].entity_type == entities[0]
        assert results[0].start == 0
        assert results[0].end == 23


    # Context should not change the result if the checksum fails
    def test_invalid_iban_with_exact_context(self):
        number = 'IL150120690000003111141'
        context = 'my iban number is '
        results = iban_recognizer.analyze(context + number, entities)

        assert len(results) == 1
        assert results[0].score == 0
        assert results[0].entity_type == entities[0]
        assert results[0].start == 18
        assert results[0].end == 41
