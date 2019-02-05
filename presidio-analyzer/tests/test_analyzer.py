from unittest import TestCase
from analyzer import AnalyzerEngine


class TestAnalyzer(TestCase):
    def test_get_recognizers_all(self):
        analyzer = AnalyzerEngine()
        text = " Credit card: 4095-2609-9393-4932,  my name is  John Oliver, DateTime: September 18     Domain: microsoft.com"
        fields = ["CREDIT_CARD", "PHONE_NUMBER", "DATE_TIME", "PERSON"]
        results = analyzer.analyze(text, fields)
        assert len(results) == 3
        assert results[0].entity_type == "CREDIT_CARD"
        assert results[1].entity_type == "DATE_TIME"
        assert results[2].entity_type == "PERSON"

