from unittest import TestCase

import json
import hashlib
import time
import pytest

from assertions import assert_result
from analyzer.analyze_pb2 import AnalyzeRequest

from analyzer import AnalyzerEngine, PatternRecognizer, Pattern, \
    RecognizerResult, RecognizerRegistry
from analyzer.predefined_recognizers import CreditCardRecognizer, \
    UsPhoneRecognizer
from analyzer.recognizer_registry.recognizers_store_api \
    import RecognizerStoreApi  # noqa: F401


class RecognizerStoreApiMock(RecognizerStoreApi):
    """
    A mock that acts as a recognizers store, allows to add and get recognizers
    """

    def __init__(self):
        self.latest_hash = ""
        self.recognizers = []

    def get_latest_hash(self):
        return self.latest_hash

    def get_all_recognizers(self):
        return self.recognizers

    def add_custom_pattern_recognizer(self, new_recognizer, skip_hash_update=False):
        patterns = []
        for pat in new_recognizer.patterns:
            patterns.extend([Pattern(pat.name, pat.regex, pat.score)])
        new_custom_recognizer = PatternRecognizer(name=new_recognizer.name, supported_entity=new_recognizer.supported_entities[0],
                                                  supported_language=new_recognizer.supported_language,
                                                  black_list=new_recognizer.black_list,
                                                  context=new_recognizer.context,
                                                  patterns=patterns)
        self.recognizers.append(new_custom_recognizer)

        if skip_hash_update:
            return

        m = hashlib.md5()
        for recognizer in self.recognizers:
            m.update(recognizer.name.encode('utf-8'))
        self.latest_hash = m.digest()

    def remove_recognizer(self, name):
        for i in self.recognizers:
            if i.name == name:
                self.recognizers.remove(i)

        m = hashlib.md5()
        for recognizer in self.recognizers:
            m.update(recognizer.name.encode('utf-8'))
        self.latest_hash = m.digest()


class MockRecognizerRegistry(RecognizerRegistry):
    """
    A mock that acts as a recognizers registry
    """

    def load_recognizers(self, path):
        #   TODO: Change the code to dynamic loading -
        # Task #598:  Support loading of the pre-defined recognizers
        # from the given path.
        self.recognizers.extend([CreditCardRecognizer(),
                                 UsPhoneRecognizer()])


class TestAnalyzerEngine(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestAnalyzerEngine, self).__init__(*args, **kwargs)
        self.loaded_registry = MockRecognizerRegistry(RecognizerStoreApiMock())
        self.loaded_analyzer_engine = AnalyzerEngine(self.loaded_registry)

    def test_analyze_with_predefined_recognizers_return_results(self):
        text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
        language = "en"
        entities = ["CREDIT_CARD"]
        results = self.loaded_analyzer_engine.analyze(text, entities, language)

        assert len(results) == 1
        assert_result(results[0], "CREDIT_CARD", 14, 33, 1.0)

    def test_analyze_with_multiple_predefined_recognizers(self):
        text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
        language = "en"
        entities = ["CREDIT_CARD", "PHONE_NUMBER"]
        results = self.loaded_analyzer_engine.analyze(text, entities, language)

        assert len(results) == 2
        assert_result(results[0], "CREDIT_CARD", 14, 33, 1.0)
        assert_result(results[1], "PHONE_NUMBER", 48, 59, 0.5)

    def test_analyze_without_entities(self):
        with pytest.raises(ValueError):
            language = "en"
            text = " Credit card: 4095-2609-9393-4932,  my name is  John Oliver, DateTime: September 18 Domain: microsoft.com"
            entities = []
            self.loaded_analyzer_engine.analyze(text, entities, language)

    def test_analyze_with_empty_text(self):
        language = "en"
        text = ""
        entities = ["CREDIT_CARD", "PHONE_NUMBER"]
        results = self.loaded_analyzer_engine.analyze(text, entities, language)

        assert len(results) == 0

    def test_analyze_with_unsupported_language(self):
        with pytest.raises(ValueError):
            language = "de"
            text = ""
            entities = ["CREDIT_CARD", "PHONE_NUMBER"]
            self.loaded_analyzer_engine.analyze(text, entities, language)

    def test_remove_duplicates(self):
        # test same result with different score will return only the highest
        arr = [RecognizerResult(start=0, end=5, score=0.1, entity_type="x"),
               RecognizerResult(start=0, end=5, score=0.5, entity_type="x")]
        results = AnalyzerEngine._AnalyzerEngine__remove_duplicates(arr)
        assert len(results) == 1
        assert results[0].score == 0.5
        # TODO: add more cases with bug:
        # bug# 597: Analyzer remove duplicates doesn't handle all cases of one result as a substring of the other

    def test_added_pattern_recognizer_works(self):
        pattern = Pattern("rocket pattern", r'\W*(rocket)\W*', 0.8)
        pattern_recognizer = PatternRecognizer("ROCKET",
                                               name="Rocket recognizer",
                                               patterns=[pattern])

        # Make sure the analyzer doesn't get this entity
        recognizers_store_api_mock = RecognizerStoreApiMock()
        analyze_engine = AnalyzerEngine(
            MockRecognizerRegistry(recognizers_store_api_mock))
        text = "rocket is my favorite transportation"
        entities = ["CREDIT_CARD", "ROCKET"]

        results = analyze_engine.analyze(text=text, entities=entities,
                                         language='en')

        assert len(results) == 0

        # Add a new recognizer for the word "rocket" (case insensitive)
        recognizers_store_api_mock.add_custom_pattern_recognizer(
            pattern_recognizer)

        # Check that the entity is recognized:
        results = analyze_engine.analyze(text=text, entities=entities,
                                         language='en')

        assert len(results) == 1
        assert_result(results[0], "ROCKET", 0, 7, 0.8)

    def test_removed_pattern_recognizer_doesnt_work(self):
        pattern = Pattern("spaceship pattern", r'\W*(spaceship)\W*', 0.8)
        pattern_recognizer = PatternRecognizer("SPACESHIP",
                                               name="Spaceship recognizer",
                                               patterns=[pattern])

        # Make sure the analyzer doesn't get this entity
        recognizers_store_api_mock = RecognizerStoreApiMock()
        analyze_engine = AnalyzerEngine(MockRecognizerRegistry(
            recognizers_store_api_mock))
        text = "spaceship is my favorite transportation"
        entities = ["CREDIT_CARD", "SPACESHIP"]

        results = analyze_engine.analyze(text=text, entities=entities,
                                         language='en')

        assert len(results) == 0

        # Add a new recognizer for the word "rocket" (case insensitive)
        recognizers_store_api_mock.add_custom_pattern_recognizer(
            pattern_recognizer)
        # Check that the entity is recognized:
        results = analyze_engine.analyze(text=text, entities=entities,
                                         language='en')
        assert len(results) == 1
        assert_result(results[0], "SPACESHIP", 0, 10, 0.8)

        # Remove recognizer
        recognizers_store_api_mock.remove_recognizer(
            "Spaceship recognizer")
        # Test again to see we didn't get any results
        results = analyze_engine.analyze(text=text, entities=entities,
                                         language='en')

        assert len(results) == 0

    def test_apply_with_language_returns_correct_response(self):
        request = AnalyzeRequest()
        request.analyzeTemplate.languageCode = 'en'
        new_field = request.analyzeTemplate.fields.add()
        new_field.name = 'CREDIT_CARD'
        new_field.minScore = '0.5'
        request.text = "My credit card number is 4916994465041084"
        response = self.loaded_analyzer_engine.Apply(request, None)

        assert response.analyzeResults is not None

    def test_apply_with_no_language_returns_default(self):
        request = AnalyzeRequest()
        request.analyzeTemplate.languageCode = ''
        new_field = request.analyzeTemplate.fields.add()
        new_field.name = 'CREDIT_CARD'
        new_field.minScore = '0.5'
        request.text = "My credit card number is 4916994465041084"
        response = self.loaded_analyzer_engine.Apply(request, None)
        assert response.analyzeResults is not None
