"""Integration test for Pseudonymize operator with AnonymizerEngine."""

import pytest

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig


# Check if Faker is available
try:
    import faker  # noqa: F401
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not FAKER_AVAILABLE,
    reason="Faker library not installed"
)


class TestPseudonymizeIntegration:
    """Integration tests for Pseudonymize operator."""

    def test_anonymize_with_pseudonymize_operator(self):
        """Test using pseudonymize operator with AnonymizerEngine."""
        engine = AnonymizerEngine()
        
        text = "My name is John Doe and my email is john.doe@example.com"
        analyzer_results = [
            RecognizerResult(entity_type="PERSON", start=11, end=19, score=0.8),
            RecognizerResult(entity_type="EMAIL_ADDRESS", start=36, end=56, score=0.8),
        ]
        
        result = engine.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators={
                "PERSON": OperatorConfig("pseudonymize", {"locale": "en_US"}),
                "EMAIL_ADDRESS": OperatorConfig("pseudonymize", {"locale": "en_US"}),
            }
        )
        
        assert result.text != text
        assert "John Doe" not in result.text
        assert "john.doe@example.com" not in result.text
        assert "@" in result.text  # Email should still have @ symbol

    def test_anonymize_with_consistent_pseudonymization(self):
        """Test consistent pseudonymization across multiple entities."""
        engine = AnonymizerEngine()
        
        text = "John Doe and John Doe are the same person"
        analyzer_results = [
            RecognizerResult(entity_type="PERSON", start=0, end=8, score=0.8),
            RecognizerResult(entity_type="PERSON", start=13, end=21, score=0.8),
        ]
        
        result = engine.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators={
                "PERSON": OperatorConfig("pseudonymize", {
                    "locale": "en_US",
                    "consistent": True,
                    "seed": 42
                }),
            }
        )
        
        # Both "John Doe" should be replaced with the same pseudonym
        parts = result.text.split(" and ")
        assert len(parts) == 2
        # The first two words should be identical (the pseudonymized names)
        first_name = " ".join(parts[0].split()[:2])
        second_name = " ".join(parts[1].split()[:2])
        assert first_name == second_name

    def test_anonymize_with_korean_locale(self):
        """Test pseudonymization with Korean locale."""
        engine = AnonymizerEngine()
        
        text = "이름은 홍길동이고 연락처는 010-1234-5678입니다"
        analyzer_results = [
            RecognizerResult(entity_type="PERSON", start=4, end=7, score=0.8),
            RecognizerResult(entity_type="PHONE_NUMBER", start=15, end=28, score=0.8),
        ]
        
        result = engine.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators={
                "PERSON": OperatorConfig("pseudonymize", {"locale": "ko_KR"}),
                "PHONE_NUMBER": OperatorConfig("pseudonymize", {"locale": "ko_KR"}),
            }
        )
        
        assert result.text != text
        assert "홍길동" not in result.text
        assert "010-1234-5678" not in result.text

    def test_anonymize_mixed_operators(self):
        """Test mixing pseudonymize with other operators."""
        engine = AnonymizerEngine()
        
        text = "My name is John Doe, SSN: 123-45-6789, email: john@example.com"
        analyzer_results = [
            RecognizerResult(entity_type="PERSON", start=11, end=19, score=0.8),
            RecognizerResult(entity_type="US_SSN", start=26, end=37, score=0.9),
            RecognizerResult(entity_type="EMAIL_ADDRESS", start=46, end=62, score=0.8),
        ]
        
        result = engine.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators={
                "PERSON": OperatorConfig("pseudonymize", {"locale": "en_US"}),
                "US_SSN": OperatorConfig("mask", {
                    "masking_char": "*",
                    "chars_to_mask": 5,
                    "from_end": True
                }),
                "EMAIL_ADDRESS": OperatorConfig("pseudonymize", {"locale": "en_US"}),
            }
        )
        
        assert "John Doe" not in result.text
        assert "*" in result.text  # SSN should be masked
        assert "john@example.com" not in result.text
        assert "@" in result.text  # Email should still have @ symbol

    def test_anonymize_with_default_operator_pseudonymize(self):
        """Test using pseudonymize as default operator."""
        engine = AnonymizerEngine()
        
        text = "Contact: John Doe, john@example.com, 555-1234"
        analyzer_results = [
            RecognizerResult(entity_type="PERSON", start=9, end=17, score=0.8),
            RecognizerResult(entity_type="EMAIL_ADDRESS", start=19, end=35, score=0.8),
            RecognizerResult(entity_type="PHONE_NUMBER", start=37, end=45, score=0.7),
        ]
        
        result = engine.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators={
                "DEFAULT": OperatorConfig("pseudonymize", {
                    "locale": "en_US",
                    "seed": 123
                }),
            }
        )
        
        assert "John Doe" not in result.text
        assert "john@example.com" not in result.text
        assert "555-1234" not in result.text

    def test_reproducible_anonymization_with_seed(self):
        """Test that using seed produces reproducible results."""
        engine1 = AnonymizerEngine()
        engine2 = AnonymizerEngine()
        
        text = "My name is Jane Smith"
        analyzer_results = [
            RecognizerResult(entity_type="PERSON", start=11, end=21, score=0.8),
        ]
        
        operators = {
            "PERSON": OperatorConfig("pseudonymize", {
                "locale": "en_US",
                "seed": 999
            })
        }
        
        result1 = engine1.anonymize(text=text, analyzer_results=analyzer_results, operators=operators)
        result2 = engine2.anonymize(text=text, analyzer_results=analyzer_results, operators=operators)
        
        assert result1.text == result2.text
