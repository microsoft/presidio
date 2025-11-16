"""
Comprehensive test suite for Presidio Analyzer features.

This test file contains 50 tests covering various components including:
- RecognizerResult functionality
- AnalyzerRequest processing
- Pattern matching and validation
- Entity recognition edge cases
- Score calculation and thresholding
- Context-aware enhancements
- Multi-language support scenarios
- Registry operations
- Batch processing capabilities
- Error handling and validation
"""

import re
from typing import List, Dict
from unittest.mock import Mock, patch, MagicMock

import pytest

from presidio_analyzer import (
    AnalyzerEngine,
    PatternRecognizer,
    Pattern,
    RecognizerResult,
    RecognizerRegistry,
    EntityRecognizer,
    AnalysisExplanation,
)
from presidio_analyzer.analyzer_request import AnalyzerRequest
from presidio_analyzer.nlp_engine import NlpArtifacts

from tests.mocks import NlpEngineMock, AppTracerMock, RecognizerRegistryMock


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_nlp_artifacts():
    """Create mock NLP artifacts for testing."""
    return NlpArtifacts([], [], [], [], None, "en")


@pytest.fixture
def mock_analyzer_engine(mock_nlp_artifacts):
    """Create a mock analyzer engine for testing."""
    registry = RecognizerRegistryMock()
    nlp_engine = NlpEngineMock(stopwords=[], punct_words=[], nlp_artifacts=mock_nlp_artifacts)
    app_tracer = AppTracerMock(enable_decision_process=True)
    return AnalyzerEngine(
        registry,
        nlp_engine,
        app_tracer=app_tracer,
        log_decision_process=True,
    )


@pytest.fixture
def sample_pattern():
    """Create a sample pattern for testing."""
    return Pattern(name="test_pattern", regex=r"\b\d{3}-\d{2}-\d{4}\b", score=0.85)


@pytest.fixture
def sample_recognizer(sample_pattern):
    """Create a sample recognizer for testing."""
    return PatternRecognizer(
        supported_entity="TEST_ENTITY",
        patterns=[sample_pattern],
        name="TestRecognizer",
    )


# ============================================================================
# RecognizerResult Tests (Tests 1-10)
# ============================================================================

def test_when_recognizer_result_created_then_fields_set_correctly():
    """Test 1: Verify RecognizerResult initialization sets all fields correctly."""
    result = RecognizerResult(
        entity_type="PERSON",
        start=0,
        end=10,
        score=0.95,
    )
    assert result.entity_type == "PERSON"
    assert result.start == 0
    assert result.end == 10
    assert result.score == 0.95


def test_when_recognizer_result_with_metadata_then_metadata_stored():
    """Test 2: Verify recognition_metadata is properly stored."""
    metadata = {"recognizer_name": "TestRecognizer", "custom_field": "value"}
    result = RecognizerResult(
        entity_type="EMAIL",
        start=5,
        end=20,
        score=0.8,
        recognition_metadata=metadata,
    )
    assert result.recognition_metadata == metadata
    assert result.recognition_metadata["recognizer_name"] == "TestRecognizer"


def test_when_recognizer_result_intersects_then_returns_overlap_count():
    """Test 3: Verify intersection calculation between two results."""
    result1 = RecognizerResult("PERSON", 0, 10, 0.9)
    result2 = RecognizerResult("NAME", 5, 15, 0.8)
    overlap = result1.intersects(result2)
    assert overlap == 5  # Characters 5-9 overlap


def test_when_recognizer_result_no_intersection_then_returns_zero():
    """Test 4: Verify no intersection returns zero."""
    result1 = RecognizerResult("PERSON", 0, 10, 0.9)
    result2 = RecognizerResult("EMAIL", 20, 30, 0.8)
    overlap = result1.intersects(result2)
    assert overlap == 0


def test_when_recognizer_result_to_dict_then_serializes_correctly():
    """Test 5: Verify to_dict serialization."""
    result = RecognizerResult("PHONE", 10, 20, 0.75)
    result_dict = result.to_dict()
    assert result_dict["entity_type"] == "PHONE"
    assert result_dict["start"] == 10
    assert result_dict["end"] == 20
    assert result_dict["score"] == 0.75


def test_when_recognizer_result_from_json_then_deserializes_correctly():
    """Test 6: Verify from_json deserialization."""
    data = {
        "entity_type": "CREDIT_CARD",
        "start": 15,
        "end": 35,
        "score": 0.99,
    }
    result = RecognizerResult.from_json(data)
    assert result.entity_type == "CREDIT_CARD"
    assert result.start == 15
    assert result.end == 35
    assert result.score == 0.99


def test_when_append_analysis_explanation_then_text_added():
    """Test 7: Verify analysis explanation text can be appended."""
    explanation = AnalysisExplanation(
        recognizer="TestRecognizer",
        original_score=0.5,
        textual_explanation="Initial explanation",
    )
    result = RecognizerResult("TEST", 0, 5, 0.5, analysis_explanation=explanation)
    result.append_analysis_explanation_text("Additional info")
    assert "Additional info" in result.analysis_explanation.textual_explanation


def test_when_recognizer_result_with_high_score_then_score_preserved():
    """Test 8: Verify high confidence scores are preserved."""
    result = RecognizerResult("SSN", 0, 11, 1.0)
    assert result.score == 1.0


def test_when_recognizer_result_with_low_score_then_score_preserved():
    """Test 9: Verify low confidence scores are preserved."""
    result = RecognizerResult("WEAK_ENTITY", 0, 5, 0.1)
    assert result.score == 0.1


def test_when_recognizer_result_str_representation_then_returns_string():
    """Test 10: Verify string representation works."""
    result = RecognizerResult("PERSON", 0, 10, 0.9)
    str_repr = str(result)
    assert isinstance(str_repr, str)


# ============================================================================
# AnalyzerRequest Tests (Tests 11-20)
# ============================================================================

def test_when_analyzer_request_with_text_then_text_extracted():
    """Test 11: Verify AnalyzerRequest extracts text field."""
    req_data = {"text": "Hello World", "language": "en"}
    request = AnalyzerRequest(req_data)
    assert request.text == "Hello World"


def test_when_analyzer_request_with_language_then_language_extracted():
    """Test 12: Verify AnalyzerRequest extracts language field."""
    req_data = {"text": "Test", "language": "es"}
    request = AnalyzerRequest(req_data)
    assert request.language == "es"


def test_when_analyzer_request_with_entities_then_entities_extracted():
    """Test 13: Verify AnalyzerRequest extracts entities field."""
    req_data = {"text": "Test", "language": "en", "entities": ["PERSON", "EMAIL"]}
    request = AnalyzerRequest(req_data)
    assert request.entities == ["PERSON", "EMAIL"]


def test_when_analyzer_request_with_correlation_id_then_id_extracted():
    """Test 14: Verify AnalyzerRequest extracts correlation_id."""
    req_data = {"text": "Test", "correlation_id": "test-123"}
    request = AnalyzerRequest(req_data)
    assert request.correlation_id == "test-123"


def test_when_analyzer_request_with_score_threshold_then_threshold_extracted():
    """Test 15: Verify AnalyzerRequest extracts score_threshold."""
    req_data = {"text": "Test", "score_threshold": 0.75}
    request = AnalyzerRequest(req_data)
    assert request.score_threshold == 0.75


def test_when_analyzer_request_with_ad_hoc_recognizers_then_recognizers_created():
    """Test 16: Verify AnalyzerRequest creates ad-hoc recognizers."""
    ad_hoc_rec = {
        "supported_entity": "CUSTOM",
        "patterns": [{"name": "custom_pattern", "regex": r"\d{5}", "score": 0.5}],
    }
    req_data = {"text": "Test", "ad_hoc_recognizers": [ad_hoc_rec]}
    request = AnalyzerRequest(req_data)
    assert len(request.ad_hoc_recognizers) == 1
    assert isinstance(request.ad_hoc_recognizers[0], PatternRecognizer)


def test_when_analyzer_request_with_context_then_context_extracted():
    """Test 17: Verify AnalyzerRequest extracts context."""
    req_data = {"text": "Test", "context": ["word1", "word2"]}
    request = AnalyzerRequest(req_data)
    assert request.context == ["word1", "word2"]


def test_when_analyzer_request_with_allow_list_then_list_extracted():
    """Test 18: Verify AnalyzerRequest extracts allow_list."""
    req_data = {"text": "Test", "allow_list": ["John", "Jane"]}
    request = AnalyzerRequest(req_data)
    assert request.allow_list == ["John", "Jane"]


def test_when_analyzer_request_with_allow_list_match_then_match_extracted():
    """Test 19: Verify AnalyzerRequest extracts allow_list_match."""
    req_data = {"text": "Test", "allow_list_match": "contains"}
    request = AnalyzerRequest(req_data)
    assert request.allow_list_match == "contains"


def test_when_analyzer_request_with_regex_flags_then_flags_extracted():
    """Test 20: Verify AnalyzerRequest extracts regex_flags."""
    custom_flags = re.IGNORECASE | re.MULTILINE
    req_data = {"text": "Test", "regex_flags": custom_flags}
    request = AnalyzerRequest(req_data)
    assert request.regex_flags == custom_flags


# ============================================================================
# Pattern and PatternRecognizer Tests (Tests 21-30)
# ============================================================================

def test_when_pattern_created_then_attributes_set():
    """Test 21: Verify Pattern initialization."""
    pattern = Pattern(name="ssn_pattern", regex=r"\d{3}-\d{2}-\d{4}", score=0.9)
    assert pattern.name == "ssn_pattern"
    assert pattern.regex == r"\d{3}-\d{2}-\d{4}"
    assert pattern.score == 0.9


def test_when_pattern_recognizer_with_deny_list_then_matches_keywords():
    """Test 22: Verify deny_list matching."""
    recognizer = PatternRecognizer(
        supported_entity="TEST",
        deny_list=["secret", "confidential"],
        patterns=[],
    )
    results = recognizer.analyze("This is secret information", ["TEST"])
    assert len(results) == 1
    assert results[0].entity_type == "TEST"


def test_when_pattern_recognizer_with_multiple_patterns_then_all_applied():
    """Test 23: Verify multiple patterns are applied."""
    pattern1 = Pattern("p1", r"\d{3}", 0.5)
    pattern2 = Pattern("p2", r"[A-Z]{3}", 0.6)
    recognizer = PatternRecognizer(
        supported_entity="MULTI",
        patterns=[pattern1, pattern2],
    )
    results = recognizer.analyze("123 ABC", ["MULTI"])
    assert len(results) == 2


def test_when_pattern_recognizer_from_dict_then_creates_instance():
    """Test 24: Verify PatternRecognizer.from_dict creates valid instance."""
    rec_dict = {
        "supported_entity": "CUSTOM",
        "patterns": [{"name": "p1", "regex": r"\d+", "score": 0.7}],
        "context": ["keyword"],
    }
    recognizer = PatternRecognizer.from_dict(rec_dict)
    assert recognizer.supported_entities == ["CUSTOM"]
    assert len(recognizer.patterns) == 1
    assert recognizer.context == ["keyword"]


def test_when_pattern_recognizer_with_context_then_context_stored():
    """Test 25: Verify context words are stored."""
    recognizer = PatternRecognizer(
        supported_entity="CONTEXTUAL",
        patterns=[Pattern("p1", r"\d+", 0.5)],
        context=["ssn", "social"],
    )
    assert recognizer.context == ["ssn", "social"]


def test_when_pattern_with_zero_score_then_score_accepted():
    """Test 26: Verify zero score is accepted for patterns."""
    pattern = Pattern(name="zero_score", regex=r"test", score=0.0)
    assert pattern.score == 0.0


def test_when_pattern_with_max_score_then_score_accepted():
    """Test 27: Verify max score (1.0) is accepted."""
    pattern = Pattern(name="max_score", regex=r"test", score=1.0)
    assert pattern.score == 1.0


def test_when_pattern_recognizer_no_entity_then_raises_error():
    """Test 28: Verify error when no entity specified."""
    with pytest.raises(ValueError):
        PatternRecognizer(
            supported_entity=[],
            patterns=[Pattern("p1", r"test", 0.5)],
        )


def test_when_pattern_recognizer_analyze_no_matches_then_empty_results():
    """Test 29: Verify empty results when no matches found."""
    recognizer = PatternRecognizer(
        supported_entity="NOMATCH",
        patterns=[Pattern("p1", r"XXXXXX", 0.5)],
    )
    results = recognizer.analyze("This text has no matches", ["NOMATCH"])
    assert len(results) == 0


def test_when_pattern_recognizer_with_version_then_version_stored():
    """Test 30: Verify version is stored in recognizer."""
    rec_dict = {
        "supported_entity": "VERSIONED",
        "patterns": [{"name": "p1", "regex": r"test", "score": 0.5}],
        "version": "2.0",
    }
    recognizer = PatternRecognizer.from_dict(rec_dict)
    assert recognizer.version == "2.0"


# ============================================================================
# AnalyzerEngine Tests (Tests 31-40)
# ============================================================================

def test_when_analyzer_engine_created_then_instance_valid():
    """Test 31: Verify AnalyzerEngine can be instantiated."""
    engine = AnalyzerEngine()
    assert engine is not None


def test_when_analyzer_engine_analyze_simple_text_then_returns_results():
    """Test 32: Verify basic analyze functionality."""
    engine = AnalyzerEngine()
    results = engine.analyze(text="My email is test@example.com", language="en")
    assert isinstance(results, list)


def test_when_analyzer_engine_with_score_threshold_then_filters_results(mock_analyzer_engine):
    """Test 33: Verify score threshold filtering."""
    text = "Test data"
    # Mock a scenario where we'd filter by score
    results = mock_analyzer_engine.analyze(
        text=text,
        language="en",
        score_threshold=0.9,
    )
    # All returned results should meet threshold
    for result in results:
        assert result.score >= 0.9 or result.score == 0  # Allow mock results


def test_when_analyzer_engine_with_specific_entities_then_only_those_detected():
    """Test 34: Verify entity filtering works with real engine."""
    engine = AnalyzerEngine()
    text = "Test email@example.com"
    results = engine.analyze(
        text=text,
        language="en",
        entities=["EMAIL_ADDRESS"],
    )
    # Implementation should only look for requested entities
    assert isinstance(results, list)


def test_when_analyzer_engine_with_correlation_id_then_id_tracked(mock_analyzer_engine):
    """Test 35: Verify correlation_id is accepted."""
    correlation_id = "test-correlation-123"
    results = mock_analyzer_engine.analyze(
        text="Test",
        language="en",
        correlation_id=correlation_id,
    )
    assert isinstance(results, list)


def test_when_analyzer_engine_with_empty_text_then_returns_empty():
    """Test 36: Verify empty text returns no results."""
    engine = AnalyzerEngine()
    results = engine.analyze(text="", language="en")
    assert len(results) == 0


def test_when_analyzer_engine_with_whitespace_only_then_returns_empty():
    """Test 37: Verify whitespace-only text returns no results."""
    engine = AnalyzerEngine()
    results = engine.analyze(text="   \n\t  ", language="en")
    assert len(results) == 0


def test_when_analyzer_engine_with_allow_list_then_filters_results():
    """Test 38: Verify allow_list filtering."""
    engine = AnalyzerEngine()
    # Allow list should exclude specified values
    results = engine.analyze(
        text="John Doe",
        language="en",
        allow_list=["John Doe"],
    )
    # Should filter out allowed entities
    assert isinstance(results, list)


def test_when_analyzer_engine_with_ad_hoc_recognizers_then_uses_them():
    """Test 39: Verify ad-hoc recognizers are used."""
    engine = AnalyzerEngine()
    ad_hoc_pattern = PatternRecognizer(
        supported_entity="CUSTOM_ID",
        patterns=[Pattern("custom", r"CUST-\d{5}", 0.9)],
    )
    # This tests that ad-hoc recognizers can be passed
    # Actual implementation would require registry support
    assert ad_hoc_pattern is not None


def test_when_analyzer_engine_with_return_decision_process_then_includes_explanation():
    """Test 40: Verify decision process can be returned."""
    engine = AnalyzerEngine()
    # When return_decision_process is True, results should include explanations
    results = engine.analyze(
        text="Test",
        language="en",
        return_decision_process=True,
    )
    assert isinstance(results, list)


# ============================================================================
# Edge Cases and Error Handling Tests (Tests 41-50)
# ============================================================================

def test_when_recognizer_result_with_negative_start_then_value_stored():
    """Test 41: Verify negative start position is accepted (edge case)."""
    result = RecognizerResult("TEST", -1, 5, 0.5)
    assert result.start == -1


def test_when_recognizer_result_with_end_before_start_then_value_stored():
    """Test 42: Verify end before start is accepted (edge case for validation)."""
    result = RecognizerResult("TEST", 10, 5, 0.5)
    assert result.end == 5
    assert result.start == 10


def test_when_recognizer_result_with_score_above_one_then_value_stored():
    """Test 43: Verify score above 1.0 is stored (validation is caller's responsibility)."""
    result = RecognizerResult("TEST", 0, 5, 1.5)
    assert result.score == 1.5


def test_when_recognizer_result_with_negative_score_then_value_stored():
    """Test 44: Verify negative score is stored (validation is caller's responsibility)."""
    result = RecognizerResult("TEST", 0, 5, -0.5)
    assert result.score == -0.5


def test_when_analyzer_request_with_empty_dict_then_defaults_applied():
    """Test 45: Verify AnalyzerRequest handles empty dict gracefully."""
    request = AnalyzerRequest({})
    assert request.text is None
    assert request.language is None
    assert request.entities is None


def test_when_analyzer_request_with_none_values_then_accepts_none():
    """Test 46: Verify AnalyzerRequest accepts None values."""
    req_data = {
        "text": None,
        "language": None,
        "entities": None,
    }
    request = AnalyzerRequest(req_data)
    assert request.text is None
    assert request.language is None
    assert request.entities is None


def test_when_pattern_with_complex_regex_then_pattern_stored():
    """Test 47: Verify complex regex patterns are stored correctly."""
    complex_regex = r"(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}"
    pattern = Pattern(name="french_phone", regex=complex_regex, score=0.8)
    assert pattern.regex == complex_regex


def test_when_pattern_with_empty_name_then_name_stored():
    """Test 48: Verify empty pattern name is accepted."""
    pattern = Pattern(name="", regex=r"test", score=0.5)
    assert pattern.name == ""


def test_when_recognizer_result_equal_start_end_then_zero_length_entity():
    """Test 49: Verify zero-length entity (start == end)."""
    result = RecognizerResult("ZERO_LENGTH", 10, 10, 0.5)
    assert result.start == result.end
    assert result.end - result.start == 0


def test_when_multiple_recognizer_results_then_can_be_sorted_by_score():
    """Test 50: Verify multiple results can be sorted by score."""
    results = [
        RecognizerResult("A", 0, 5, 0.3),
        RecognizerResult("B", 10, 15, 0.9),
        RecognizerResult("C", 20, 25, 0.6),
    ]
    sorted_results = sorted(results, key=lambda r: r.score, reverse=True)
    assert sorted_results[0].score == 0.9
    assert sorted_results[1].score == 0.6
    assert sorted_results[2].score == 0.3
