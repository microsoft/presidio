"""Tests for HuggingFaceNerRecognizer."""

import pytest
from unittest.mock import MagicMock, patch

from presidio_analyzer.predefined_recognizers import HuggingFaceNerRecognizer


@pytest.fixture
def mock_transformers_pipeline():
    """Fixture to mock HuggingFace transformers pipeline."""
    pytest.importorskip("transformers", reason="transformers package is not installed")

    mock_pipeline_instance = MagicMock()

    with patch(
        "presidio_analyzer.predefined_recognizers.ner."
        "huggingface_ner_recognizer.hf_pipeline",
        return_value=mock_pipeline_instance,
    ):
        yield mock_pipeline_instance


def test_analyze_person_name(mock_transformers_pipeline):
    """Test detection of person name."""
    # Mock HuggingFace pipeline output
    mock_transformers_pipeline.return_value = [
        {"entity_group": "PER", "start": 11, "end": 19, "score": 0.95},
    ]

    recognizer = HuggingFaceNerRecognizer(
        model_name="dslim/bert-base-NER",
        supported_language="en"
    )
    recognizer.ner_pipeline = mock_transformers_pipeline

    text = "My name is John Doe and my phone is 555-1234"
    entities = ["PERSON"]

    results = recognizer.analyze(text, entities)

    assert len(results) == 1
    assert results[0].entity_type == "PERSON"
    assert results[0].start == 11
    assert results[0].end == 19
    assert results[0].score == pytest.approx(0.95, rel=1e-2)


def test_analyze_korean_with_particles(mock_transformers_pipeline):
    """Test detection in Korean text with particles (agglutinative language)."""
    # Mock HuggingFace pipeline output - returns clean entity without particle
    mock_transformers_pipeline.return_value = [
        {"entity_group": "PS", "start": 6, "end": 9, "score": 0.95},
    ]

    recognizer = HuggingFaceNerRecognizer(
        model_name="Leo97/KoELECTRA-small-v3-modu-ner",
        supported_language="ko"
    )
    recognizer.ner_pipeline = mock_transformers_pipeline

    # "김태웅이고" contains name + particle, but NER returns only "김태웅"
    text = "내 이름은 김태웅이고 전화번호는 010-1234-5678이야"
    entities = ["PERSON"]

    results = recognizer.analyze(text, entities)

    assert len(results) == 1
    assert results[0].entity_type == "PERSON"
    assert results[0].start == 6
    assert results[0].end == 9
    assert results[0].score == pytest.approx(0.95, rel=1e-2)


def test_analyze_multiple_entities(mock_transformers_pipeline):
    """Test detection of multiple entity types."""
    mock_transformers_pipeline.return_value = [
        {"entity_group": "PER", "start": 0, "end": 8, "score": 0.92},
        {"entity_group": "LOC", "start": 20, "end": 28, "score": 0.88},
        {"entity_group": "ORG", "start": 40, "end": 49, "score": 0.85},
    ]

    recognizer = HuggingFaceNerRecognizer(
        model_name="dslim/bert-base-NER",
        supported_language="en"
    )
    recognizer.ner_pipeline = mock_transformers_pipeline

    text = "John Doe lives in New York and works at Microsoft"
    entities = ["PERSON", "LOCATION", "ORGANIZATION"]

    results = recognizer.analyze(text, entities)

    assert len(results) == 3
    assert results[0].entity_type == "PERSON"
    assert results[1].entity_type == "LOCATION"
    assert results[2].entity_type == "ORGANIZATION"


def test_analyze_filters_low_confidence(mock_transformers_pipeline):
    """Test that low confidence predictions are filtered out."""
    mock_transformers_pipeline.return_value = [
        {"entity_group": "PER", "start": 0, "end": 8, "score": 0.3},  # Below threshold
        {"entity_group": "PER", "start": 13, "end": 21, "score": 0.9},  # Above threshold
    ]

    recognizer = HuggingFaceNerRecognizer(
        model_name="dslim/bert-base-NER",
        threshold=0.5
    )
    recognizer.ner_pipeline = mock_transformers_pipeline

    text = "John Doe and Jane Doe"
    entities = ["PERSON"]

    results = recognizer.analyze(text, entities)

    # Only the high confidence result should be returned
    assert len(results) == 1
    assert results[0].score == pytest.approx(0.9, rel=1e-2)


def test_analyze_with_custom_label_mapping(mock_transformers_pipeline):
    """Test custom label mapping."""
    mock_transformers_pipeline.return_value = [
        {"entity_group": "CUSTOM_PERSON", "start": 0, "end": 8, "score": 0.90},
    ]

    custom_mapping = {"CUSTOM_PERSON": "PERSON"}
    recognizer = HuggingFaceNerRecognizer(
        model_name="custom/model",
        label_mapping=custom_mapping
    )
    recognizer.ner_pipeline = mock_transformers_pipeline

    text = "John Doe is here"
    entities = ["PERSON"]

    results = recognizer.analyze(text, entities)

    assert len(results) == 1
    assert results[0].entity_type == "PERSON"


def test_analyze_filters_unsupported_entities(mock_transformers_pipeline):
    """Test that unsupported entities are filtered out."""
    mock_transformers_pipeline.return_value = [
        {"entity_group": "PER", "start": 0, "end": 8, "score": 0.95},
    ]

    recognizer = HuggingFaceNerRecognizer(model_name="dslim/bert-base-NER")
    recognizer.ner_pipeline = mock_transformers_pipeline

    text = "John Doe is here"
    entities = ["LOCATION"]  # Only looking for LOCATION, not PERSON

    results = recognizer.analyze(text, entities)

    # Should filter out PERSON since we only requested LOCATION
    assert len(results) == 0


def test_analyze_empty_text(mock_transformers_pipeline):
    """Test handling of empty text."""
    recognizer = HuggingFaceNerRecognizer(model_name="dslim/bert-base-NER")
    recognizer.ner_pipeline = mock_transformers_pipeline

    results = recognizer.analyze("", ["PERSON"])
    assert len(results) == 0

    results = recognizer.analyze("   ", ["PERSON"])
    assert len(results) == 0


def test_analyze_no_entities_found(mock_transformers_pipeline):
    """Test when no entities are found."""
    mock_transformers_pipeline.return_value = []

    recognizer = HuggingFaceNerRecognizer(model_name="dslim/bert-base-NER")
    recognizer.ner_pipeline = mock_transformers_pipeline

    text = "No entities in this text"
    entities = ["PERSON", "LOCATION"]

    results = recognizer.analyze(text, entities)

    assert len(results) == 0


def test_default_supported_language():
    """Test that default supported language is English."""
    recognizer = HuggingFaceNerRecognizer(model_name="dslim/bert-base-NER")
    assert recognizer.supported_language == "en"


def test_custom_supported_language():
    """Test setting custom supported language."""
    recognizer = HuggingFaceNerRecognizer(
        model_name="Leo97/KoELECTRA-small-v3-modu-ner",
        supported_language="ko"
    )
    assert recognizer.supported_language == "ko"


def test_supported_entities_from_label_mapping():
    """Test that supported entities are derived from label mapping."""
    recognizer = HuggingFaceNerRecognizer(model_name="dslim/bert-base-NER")
    # Should include standard Presidio entities from DEFAULT_LABEL_MAPPING
    assert "PERSON" in recognizer.supported_entities
    assert "LOCATION" in recognizer.supported_entities
    assert "ORGANIZATION" in recognizer.supported_entities


def test_load_requires_model_name():
    """Test that load() raises error if model_name not set."""
    recognizer = HuggingFaceNerRecognizer()  # No model_name

    with pytest.raises(ValueError, match="model_name must be set"):
        recognizer.load()
