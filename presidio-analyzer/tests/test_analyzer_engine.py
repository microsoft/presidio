from unittest import TestCase

import pytest

from analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from analyzer import RecognizerResult



class TestAnalyzerEngine(TestCase):

    def test_analyze_with_predefined_recognizers_return_results(self):
        analyze_engine = AnalyzerEngine()
        text = " Credit card: 4095-2609-9393-4932,  my name is  John Oliver, DateTime: September 18 " \
               "Domain: microsoft.com"
        langauge = "en"
        entities = ["CREDIT_CARD", "PHONE_NUMBER", "DATE_TIME", "PERSON"]
        results = analyze_engine.analyze(text, entities, langauge)
        assert len(results) == 3
        assert results[0].entity_type == "CREDIT_CARD"
        assert results[0].score == 1.0
        assert results[0].start == 14
        assert results[0].end == 33

        assert results[1].entity_type == "PERSON"
        assert results[1].score == 0.85
        assert results[1].start == 48
        assert results[1].end == 59

        assert results[2].entity_type == "DATE_TIME"
        assert results[2].score == 0.85
        assert results[2].start == 71
        assert results[2].end == 83

        entities = ["CREDIT_CARD"]
        results = analyze_engine.analyze(text, entities, LANGUAGE)
        assert len(results) == 1
        assert results[0].entity_type == "CREDIT_CARD"
        assert results[0].score == 1.0
        assert results[0].start == 14
        assert results[0].end == 33

    def test_analyze_without_entities(self):
        with pytest.raises(ValueError):
            langauge = "en"
            analyze_engine = AnalyzerEngine()
            text = " Credit card: 4095-2609-9393-4932,  my name is  John Oliver, DateTime: September 18 " \
                   "Domain: microsoft.com"
            entities = []
            analyze_engine.analyze(text, entities, langauge)

    def test_analyze_with_empty_text(self):
        analyze_engine = AnalyzerEngine()
        langauge = "en"
        text = ""
        entities = ["CREDIT_CARD", "PERSON"]
        results = analyze_engine.analyze(text, entities, langauge)
        assert len(results) == 0

    def test_analyze_with_unsupported_language(self):
        with pytest.raises(ValueError):
            langauge = "de"
            analyze_engine = AnalyzerEngine()
            text = ""
            entities = ["CREDIT_CARD", "PERSON"]
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
        analyze_engine = AnalyzerEngine()
        text = "rocket is my favorite transportation"
        entities = ["CREDIT_CARD", "ROCKET"]

        res = analyze_engine.analyze(text=text, entities=entities, language='en')

        assert len(res) == 0

        # Add a new recognizer for the word "rocket" (case insensitive)
        analyze_engine.add_pattern_recognizer(pattern_recognizer.to_dict())

        # Check that the entity is recognized:
        res = analyze_engine.analyze(text=text, entities=entities, language='en')
        assert res[0].start == 0
        assert res[0].end == 7


    def test_remove_analyzer(self):
        pattern = Pattern("spaceship pattern", r'\W*(spaceship)\W*', 0.8)
        pattern_recognizer = PatternRecognizer("SPACESHIP",
                                               name="Spaceship recognizer",
                                               patterns=[pattern])

        # Make sure the analyzer doesn't get this entity
        analyze_engine = AnalyzerEngine()
        text = "spaceship is my favorite transportation"
        entities = ["CREDIT_CARD", "SPACESHIP"]

        res = analyze_engine.analyze(text=text, entities=entities, language='en')

        assert len(res) == 0

        # Add a new recognizer for the word "rocket" (case insensitive)
        analyze_engine.add_pattern_recognizer(pattern_recognizer.to_dict())

        # Check that the entity is recognized:
        res = analyze_engine.analyze(text=text, entities=entities, language='en')
        assert res[0].start == 0
        assert res[0].end == 10

        # Remove recognizer
        analyze_engine.remove_recognizer("Spaceship recognizer")

        # Test again to see we didn't get any results
        res = analyze_engine.analyze(text=text, entities=entities, language='en')

        assert len(res) == 0
