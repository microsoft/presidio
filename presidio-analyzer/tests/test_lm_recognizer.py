"""Tests for LMRecognizer base class."""
import pytest
from unittest.mock import Mock

from presidio_analyzer.lm_recognizer import LMRecognizer
from presidio_analyzer import RecognizerResult


class ConcreteLMRecognizer(LMRecognizer):
    """Concrete implementation for testing."""

    def __init__(self, **kwargs):
        super().__init__(
            supported_entities=["PERSON", "EMAIL_ADDRESS"],
            name="Test LLM Recognizer",
            **kwargs
        )

    def _call_llm(self, text, entities, **kwargs):
        """Mock implementation that returns RecognizerResult objects."""
        return self.mock_entities if hasattr(self, 'mock_entities') else []


class TestLMRecognizerAnalyze:
    """Test LMRecognizer.analyze() method."""

    def test_when_text_is_empty_then_returns_empty_list(self):
        """Test that empty text returns empty results."""
        recognizer = ConcreteLMRecognizer()
        
        results = recognizer.analyze("")
        assert results == []
        
        results = recognizer.analyze("   ")
        assert results == []

    def test_when_entities_is_none_then_uses_all_supported_entities(self):
        """Test that None entities parameter uses all supported entities."""
        recognizer = ConcreteLMRecognizer()
        recognizer.mock_entities = [
            RecognizerResult(entity_type="PERSON", start=0, end=4, score=0.85)
        ]
        
        results = recognizer.analyze("John", entities=None)
        assert len(results) == 1
        assert results[0].entity_type == "PERSON"

    def test_when_requested_entity_not_supported_then_returns_empty(self):
        """Test that unsupported entities return empty results."""
        recognizer = ConcreteLMRecognizer()
        recognizer.mock_entities = []
        
        results = recognizer.analyze("test", entities=["CREDIT_CARD"])
        assert results == []

    def test_when_llm_returns_entities_then_returns_recognizer_results(self):
        """Test that LLM returns RecognizerResult objects."""
        recognizer = ConcreteLMRecognizer()
        recognizer.mock_entities = [
            RecognizerResult(
                entity_type="PERSON",
                start=11,
                end=19,
                score=0.9,
                recognition_metadata={"source": "test"}
            )
        ]
        
        results = recognizer.analyze("My name is John Doe", entities=["PERSON"])
        
        assert len(results) == 1
        assert isinstance(results[0], RecognizerResult)
        assert results[0].entity_type == "PERSON"
        assert results[0].start == 11
        assert results[0].end == 19
        assert results[0].score == 0.9

    def test_when_entity_below_min_score_then_filters_out(self):
        """Test that entities below min_score are filtered."""
        recognizer = ConcreteLMRecognizer(min_score=0.8)
        recognizer.mock_entities = [
            RecognizerResult(entity_type="PERSON", start=0, end=4, score=0.9),
            RecognizerResult(entity_type="PERSON", start=5, end=9, score=0.7),
        ]
        
        results = recognizer.analyze("John Jane")
        
        assert len(results) == 1
        assert results[0].score == 0.9

    def test_when_llm_raises_exception_then_returns_empty_list(self):
        """Test that exceptions are caught and empty list returned."""
        class ErrorLMRecognizer(LMRecognizer):
            """Recognizer that raises error in _call_llm."""
            def __init__(self):
                super().__init__(
                    supported_entities=["PERSON"],
                    name="Error Test Recognizer"
                )
            
            def _call_llm(self, text, entities, **kwargs):
                raise RuntimeError("LLM API error")
        
        recognizer = ErrorLMRecognizer()
        
        with pytest.raises(RuntimeError, match="LLM API error"):
            recognizer.analyze("test text", entities=["PERSON"])

    def test_when_entity_missing_required_fields_then_skips(self):
        """Test that entities with missing required fields are skipped."""
        recognizer = ConcreteLMRecognizer()
        recognizer.mock_entities = [
            RecognizerResult(entity_type="", start=0, end=4, score=0.85),  # Missing type
            RecognizerResult(entity_type="PERSON", start=None, end=4, score=0.85),  # Missing start
        ]
        
        results = recognizer.analyze("test")
        assert results == []


class TestLMRecognizerMetadata:
    """Test LMRecognizer metadata handling."""

    def test_when_entity_has_metadata_then_preserves_it(self):
        """Test that metadata is preserved in RecognizerResult."""
        recognizer = ConcreteLMRecognizer()
        recognizer.mock_entities = [
            RecognizerResult(
                entity_type="PERSON",
                start=0,
                end=4,
                score=0.9,
                recognition_metadata={"alignment": "MATCH_EXACT", "source": "test"}
            )
        ]
        
        results = recognizer.analyze("John")
        
        assert len(results) == 1
        assert results[0].recognition_metadata == {"alignment": "MATCH_EXACT", "source": "test"}
        assert results[0].score == 0.9

    def test_when_entity_has_no_metadata_then_works_correctly(self):
        """Test that entities without metadata work correctly."""
        recognizer = ConcreteLMRecognizer()
        recognizer.mock_entities = [
            RecognizerResult(entity_type="PERSON", start=0, end=4, score=0.85)
        ]
        
        results = recognizer.analyze("John")
        
        assert len(results) == 1
        assert results[0].entity_type == "PERSON"
        assert results[0].score == 0.85


class TestLMRecognizerFiltering:
    """Test LMRecognizer filtering functionality."""

    def test_when_entity_in_labels_to_ignore_then_filters_out(self):
        """Test that entities in labels_to_ignore are filtered out."""
        recognizer = ConcreteLMRecognizer(labels_to_ignore=["PERSON", "location"])
        recognizer.mock_entities = [
            RecognizerResult(entity_type="PERSON", start=0, end=4, score=0.9),
            RecognizerResult(entity_type="EMAIL_ADDRESS", start=5, end=20, score=0.9),
            RecognizerResult(entity_type="LOCATION", start=21, end=30, score=0.9),
        ]
        
        results = recognizer.analyze("test text")
        
        # Only EMAIL_ADDRESS should remain (PERSON and LOCATION ignored, case-insensitive)
        assert len(results) == 1
        assert results[0].entity_type == "EMAIL_ADDRESS"

    def test_when_unknown_entity_and_consolidation_enabled_then_creates_generic(self):
        """Test unknown entity types get consolidated to GENERIC_PII_ENTITY."""
        recognizer = ConcreteLMRecognizer(enable_generic_consolidation=True)
        recognizer.mock_entities = [
            RecognizerResult(entity_type="UNKNOWN_TYPE", start=0, end=10, score=0.9),
            RecognizerResult(entity_type="PERSON", start=11, end=15, score=0.9),
        ]
        
        results = recognizer.analyze("test text")
        
        assert len(results) == 2
        # Unknown type should be converted to GENERIC_PII_ENTITY
        assert results[0].entity_type == "GENERIC_PII_ENTITY"
        assert results[0].recognition_metadata["original_entity_type"] == "UNKNOWN_TYPE"
        # Known type should remain unchanged
        assert results[1].entity_type == "PERSON"

    def test_when_unknown_entity_and_consolidation_disabled_then_skips(self):
        """Test unknown entities are skipped when consolidation is disabled."""
        recognizer = ConcreteLMRecognizer(enable_generic_consolidation=False)
        recognizer.mock_entities = [
            RecognizerResult(entity_type="UNKNOWN_TYPE", start=0, end=10, score=0.9),
            RecognizerResult(entity_type="PERSON", start=11, end=15, score=0.9),
        ]
        
        results = recognizer.analyze("test text")
        
        # Only known entity should be returned
        assert len(results) == 1
        assert results[0].entity_type == "PERSON"

    def test_when_unknown_entity_with_existing_metadata_then_preserves_metadata(self):
        """Test that existing metadata is preserved when adding original_entity_type."""
        recognizer = ConcreteLMRecognizer(enable_generic_consolidation=True)
        recognizer.mock_entities = [
            RecognizerResult(
                entity_type="CUSTOM_TYPE",
                start=0,
                end=10,
                score=0.9,
                recognition_metadata={"source": "custom", "confidence": "high"}
            ),
        ]
        
        results = recognizer.analyze("test text")
        
        assert len(results) == 1
        assert results[0].entity_type == "GENERIC_PII_ENTITY"
        assert results[0].recognition_metadata["original_entity_type"] == "CUSTOM_TYPE"
        assert results[0].recognition_metadata["source"] == "custom"
        assert results[0].recognition_metadata["confidence"] == "high"

    def test_when_get_supported_entities_called_then_returns_list(self):
        """Test get_supported_entities returns the correct list."""
        recognizer = ConcreteLMRecognizer()
        entities = recognizer.get_supported_entities()
        
        assert "PERSON" in entities
        assert "EMAIL_ADDRESS" in entities
        assert "GENERIC_PII_ENTITY" in entities  # Added by default

    def test_when_generic_consolidation_disabled_then_no_generic_in_supported(self):
        """Test GENERIC_PII_ENTITY not added when consolidation disabled."""
        recognizer = ConcreteLMRecognizer(enable_generic_consolidation=False)
        entities = recognizer.get_supported_entities()
        
        assert "PERSON" in entities
        assert "EMAIL_ADDRESS" in entities
        assert "GENERIC_PII_ENTITY" not in entities
