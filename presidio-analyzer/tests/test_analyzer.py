from unittest import TestCase
from analyzer import AnalyzerEngine
from analyzer import RecognizerResult
import pytest

LANGUAGE = "en"


class TestAnalyzer(TestCase):

    def test_analyze_with_predefined_recognizers_return_results(self):
        analyze_engine = AnalyzerEngine()
        text = " Credit card: 4095-2609-9393-4932,  my name is  John Oliver, DateTime: September 18 " \
               "Domain: microsoft.com"
        fields = ["CREDIT_CARD", "PHONE_NUMBER", "DATE_TIME", "PERSON"]
        results = analyze_engine.analyze(text, fields, LANGUAGE)
        assert len(results) == 3
        assert results[0].entity_type == "CREDIT_CARD"
        assert results[1].entity_type == "DATE_TIME"
        assert results[2].entity_type == "PERSON"

        fields = ["CREDIT_CARD"]
        results = analyze_engine.analyze(text, fields, LANGUAGE)
        assert len(results) == 1
        assert results[0].entity_type == "CREDIT_CARD"

    def test_analyze_without_entities(self):
        analyze_engine = AnalyzerEngine()
        text = " Credit card: 4095-2609-9393-4932,  my name is  John Oliver, DateTime: September 18 " \
               "Domain: microsoft.com"
        fields = []
        results = analyze_engine.analyze(text, fields, LANGUAGE)
        assert len(results) == 0

    def test_analyze_with_empty_text(self):
        analyze_engine = AnalyzerEngine()
        text = ""
        fields = ["CREDIT_CARD", "PERSON"]
        results = analyze_engine.analyze(text, fields, LANGUAGE)
        assert len(results) == 0

    def test_analyze_with_not_supported_language(self):
        with pytest.raises(ValueError):
            analyze_engine = AnalyzerEngine()
            text = ""
            fields = ["CREDIT_CARD", "PERSON"]
            results = analyze_engine.analyze(text, fields, "de")

    def test_remove_duplicates(self):
        # test same result with different score will return only the highest
        arr = [RecognizerResult(start=0, end=5, score=0.1, entity_type="x"),
               RecognizerResult(start=0, end=5, score=0.5, entity_type="x")]
        results = AnalyzerEngine._AnalyzerEngine__remove_duplicates(arr)

        assert len(results) == 1
        assert results[0].score == 0.5

        #WIP
        # # test substring with higher score will be returned
        # arr = [RecognizerResult(start=0, end=5, score=0.1, entity_type="x"),
        #        RecognizerResult(start=2, end=3, score=0.5, entity_type="x")]
        # results = AnalyzerEngine._AnalyzerEngine__remove_duplicates(arr)

        # assert len(results) == 1
        # assert results[0].score == 0.5
