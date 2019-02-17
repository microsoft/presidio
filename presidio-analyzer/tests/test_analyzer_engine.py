from unittest import TestCase

import pytest

from assertions import assert_result
from analyzer import AnalyzerEngine, PatternRecognizer, Pattern, \
    RecognizerResult, RecognizerRegistry
from analyzer.predefined_recognizers import CreditCardRecognizer, \
    UsPhoneRecognizer


class MockRecognizerRegistry(RecognizerRegistry):
    def load_recognizers(self, path):
        #   TODO: Change the code to dynamic loading -
        # Task #598:  Support loading of the pre-defined recognizers
        # from the given path.
        self.recognizers.extend([CreditCardRecognizer(),
                                 UsPhoneRecognizer()])

class TestAnalyzerEngine(TestCase):

    def test_analyze_with_single_predefined_recognizers(self):
        analyze_engine = AnalyzerEngine(MockRecognizerRegistry())
        text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
        langauge = "en"
        entities = ["CREDIT_CARD"]
        results = analyze_engine.analyze(text, entities, langauge)
       
        assert len(results) == 1
        assert_result(results[0], "CREDIT_CARD", 14, 33, 1.0)

    def test_analyze_with_multiple_predefined_recognizers(self):
        analyze_engine = AnalyzerEngine(MockRecognizerRegistry())
        text = " Credit card: 4095-2609-9393-4932,  my phone is 425 8829090"
        langauge = "en"
        entities = ["CREDIT_CARD", "PHONE_NUMBER"]
        results = analyze_engine.analyze(text, entities, langauge)
       
        assert len(results) == 2
        assert_result(results[0], "CREDIT_CARD", 14, 33, 1.0)
        assert_result(results[1], "PHONE_NUMBER", 48, 59, 0.5)

    def test_analyze_without_entities(self):
        with pytest.raises(ValueError):
            langauge = "en"
            analyze_engine = AnalyzerEngine(MockRecognizerRegistry())
            text = " Credit card: 4095-2609-9393-4932,  my name is  John Oliver, DateTime: September 18 " \
                   "Domain: microsoft.com"
            entities = []
            analyze_engine.analyze(text, entities, langauge)

    def test_analyze_with_empty_text(self):
        analyze_engine = AnalyzerEngine(MockRecognizerRegistry())
        langauge = "en"
        text = ""
        entities = ["CREDIT_CARD", "PHONE_NUMBER"]
        results = analyze_engine.analyze(text, entities, langauge)
        
        assert len(results) == 0

    def test_analyze_with_unsupported_language(self):
        with pytest.raises(ValueError):
            langauge = "de"
            analyze_engine = AnalyzerEngine(MockRecognizerRegistry())
            text = ""
            entities = ["CREDIT_CARD", "PHONE_NUMBER"]
            analyze_engine.analyze(text, entities, "de")

    def test_remove_duplicates(self):
        # test same result with different score will return only the highest
        arr = [RecognizerResult(start=0, end=5, score=0.1, entity_type="x"),
               RecognizerResult(start=0, end=5, score=0.5, entity_type="x")]
        results = AnalyzerEngine._AnalyzerEngine__remove_duplicates(arr)

        assert len(results) == 1
        assert results[0].score == 0.5

        # TODO: add more cases with bug:
        # bug# 597: Analyzer remove duplicates doesn't handle all cases of one result as a substring of the other

    def test_add_pattern_recognizer_from_dict(self):
        pattern = Pattern("rocket pattern", r'\W*(rocket)\W*', 0.8)
        pattern_recognizer = PatternRecognizer("ROCKET",
                                               name="Rocket recognizer",
                                               patterns=[pattern])

        # Make sure the analyzer doesn't get this entity
        analyze_engine = AnalyzerEngine(MockRecognizerRegistry())
        text = "rocket is my favorite transportation"
        entities = ["CREDIT_CARD", "ROCKET"]

        results = analyze_engine.analyze(text=text, entities=entities,
                                     language='en')

        assert len(results) == 0

        # Add a new recognizer for the word "rocket" (case insensitive)
        analyze_engine.add_pattern_recognizer(pattern_recognizer.to_dict())

        # Check that the entity is recognized:
        results = analyze_engine.analyze(text=text, entities=entities,
                                     language='en')
        
        assert len(results) == 1
        assert_result(results[0], "ROCKET", 0, 7, 0.8)

    def test_remove_analyzer(self):
        pattern = Pattern("spaceship pattern", r'\W*(spaceship)\W*', 0.8)
        pattern_recognizer = PatternRecognizer("SPACESHIP",
                                               name="Spaceship recognizer",
                                               patterns=[pattern])

        # Make sure the analyzer doesn't get this entity
        analyze_engine = AnalyzerEngine(MockRecognizerRegistry())
        text = "spaceship is my favorite transportation"
        entities = ["CREDIT_CARD", "SPACESHIP"]

        results = analyze_engine.analyze(text=text, entities=entities,
                                     language='en')

        assert len(results) == 0

        # Add a new recognizer for the word "rocket" (case insensitive)
        analyze_engine.add_pattern_recognizer(pattern_recognizer.to_dict())

        # Check that the entity is recognized:
        results = analyze_engine.analyze(text=text, entities=entities,
                                     language='en')
        assert len(results) == 1
        assert_result(results[0], "SPACESHIP", 0, 10, 0.8)

        # Remove recognizer
        analyze_engine.remove_recognizer("Spaceship recognizer")

        # Test again to see we didn't get any results
        results = analyze_engine.analyze(text=text, entities=entities,
                                     language='en')

        assert len(results) == 0
