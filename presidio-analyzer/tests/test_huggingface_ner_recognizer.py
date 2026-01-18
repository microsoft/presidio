"""Tests for HuggingFaceNerRecognizer."""

from unittest.mock import MagicMock, patch

import pytest
from presidio_analyzer.predefined_recognizers import HuggingFaceNerRecognizer

# Path to mock the HuggingFace pipeline import
HF_PIPELINE_PATH = (
    "presidio_analyzer.predefined_recognizers.ner."
    "huggingface_ner_recognizer.hf_pipeline"
)


@pytest.fixture
def mock_transformers_pipeline():
    """Fixture to mock HuggingFace transformers pipeline."""
    mock_pipeline_instance = MagicMock()

    with patch(HF_PIPELINE_PATH, return_value=mock_pipeline_instance):
        mock_pipeline_instance.tokenizer = MagicMock()
        yield mock_pipeline_instance


def test_analyze_person_name(mock_transformers_pipeline):
    """Test detection of person name."""
    # Mock HuggingFace pipeline output
    mock_transformers_pipeline.return_value = [
        [{"entity_group": "PER", "start": 11, "end": 23, "score": 0.95}],
    ]

    recognizer = HuggingFaceNerRecognizer(
        model_name="dslim/bert-base-NER",
        supported_language="en"
    )
    recognizer.ner_pipeline = mock_transformers_pipeline

    text = "My name is Taewoong Kim and my phone is 555-1234"
    entities = ["PERSON"]

    results = recognizer.analyze(text, entities)

    assert len(results) == 1
    assert results[0].entity_type == "PERSON"
    assert results[0].start == text.index("Taewoong Kim")
    assert results[0].end == text.index("Taewoong Kim") + len("Taewoong Kim")
    assert results[0].score == pytest.approx(0.95, rel=1e-2)


def test_analyze_korean_with_particles(mock_transformers_pipeline):
    """Test detection in Korean text with particles (agglutinative language)."""
    # Mock HuggingFace pipeline output - returns clean entity without particle
    mock_transformers_pipeline.return_value = [
        [{"entity_group": "PS", "start": 6, "end": 9, "score": 0.95}],
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
    assert results[0].start == text.index("김태웅")
    assert results[0].end == text.index("김태웅") + len("김태웅")
    assert results[0].score == pytest.approx(0.95, rel=1e-2)


def test_analyze_multiple_entities(mock_transformers_pipeline):
    """Test detection of multiple entity types."""
    mock_transformers_pipeline.return_value = [
        [
            {"entity_group": "PER", "start": 0, "end": 12, "score": 0.92},
            {"entity_group": "LOC", "start": 22, "end": 30, "score": 0.88},
            {"entity_group": "ORG", "start": 44, "end": 53, "score": 0.85},
        ]
    ]

    recognizer = HuggingFaceNerRecognizer(
        model_name="dslim/bert-base-NER",
        supported_language="en"
    )
    recognizer.ner_pipeline = mock_transformers_pipeline

    text = "Taewoong Kim lives in New York and works at Microsoft"
    entities = ["PERSON", "LOCATION", "ORGANIZATION"]

    results = recognizer.analyze(text, entities)

    assert len(results) == 3
    # Sort by start index to ensure test stability
    results.sort(key=lambda x: x.start)
    assert results[0].entity_type == "PERSON"
    assert results[1].entity_type == "LOCATION"
    assert results[2].entity_type == "ORGANIZATION"


def test_analyze_filters_low_confidence(mock_transformers_pipeline):
    """Test that low confidence predictions are filtered out."""
    mock_transformers_pipeline.return_value = [
        [
            {"entity_group": "PER", "start": 0, "end": 12, "score": 0.3},
            {"entity_group": "PER", "start": 17, "end": 25, "score": 0.9},
        ]
    ]

    recognizer = HuggingFaceNerRecognizer(
        model_name="dslim/bert-base-NER",
        threshold=0.5
    )
    recognizer.ner_pipeline = mock_transformers_pipeline

    text = "Taewoong Kim and Jane Doe"
    entities = ["PERSON"]

    results = recognizer.analyze(text, entities)

    # Only the high confidence result should be returned
    assert len(results) == 1
    assert results[0].score == pytest.approx(0.9, rel=1e-2)


def test_analyze_with_custom_label_mapping(mock_transformers_pipeline):
    """Test custom label mapping."""
    mock_transformers_pipeline.return_value = [
        [{"entity_group": "CUSTOM_PERSON", "start": 0, "end": 12, "score": 0.90}],
    ]

    custom_mapping = {"CUSTOM_PERSON": "PERSON"}
    recognizer = HuggingFaceNerRecognizer(
        model_name="custom/model",
        label_mapping=custom_mapping
    )
    recognizer.ner_pipeline = mock_transformers_pipeline

    text = "Taewoong Kim is here"
    entities = ["PERSON"]

    results = recognizer.analyze(text, entities)

    assert len(results) == 1
    assert results[0].entity_type == "PERSON"


def test_analyze_filters_unsupported_entities(mock_transformers_pipeline):
    """Test that unsupported entities are filtered out."""
    mock_transformers_pipeline.return_value = [
        [{"entity_group": "PER", "start": 0, "end": 12, "score": 0.95}],
    ]

    recognizer = HuggingFaceNerRecognizer(model_name="dslim/bert-base-NER")
    recognizer.ner_pipeline = mock_transformers_pipeline

    text = "Taewoong Kim is here"
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
    mock_transformers_pipeline.return_value = [[]]

    recognizer = HuggingFaceNerRecognizer(model_name="dslim/bert-base-NER")
    recognizer.ner_pipeline = mock_transformers_pipeline

    text = "No entities in this text"
    entities = ["PERSON", "LOCATION"]

    results = recognizer.analyze(text, entities)

    assert len(results) == 0


@patch(HF_PIPELINE_PATH, return_value=MagicMock())
def test_default_supported_language(_mock_pipeline):
    """Test that default supported language is English."""
    recognizer = HuggingFaceNerRecognizer(model_name="dslim/bert-base-NER")
    assert recognizer.supported_language == "en"


@patch(HF_PIPELINE_PATH, return_value=MagicMock())
def test_custom_supported_language(_mock_pipeline):
    """Test setting custom supported language."""
    recognizer = HuggingFaceNerRecognizer(
        model_name="Leo97/KoELECTRA-small-v3-modu-ner",
        supported_language="ko"
    )
    assert recognizer.supported_language == "ko"


@patch(HF_PIPELINE_PATH, return_value=MagicMock())
def test_supported_entities_from_label_mapping(_mock_pipeline):
    """Test that supported entities are derived from label mapping."""
    recognizer = HuggingFaceNerRecognizer(model_name="dslim/bert-base-NER")
    # Should include standard Presidio entities from DEFAULT_LABEL_MAPPING
    assert "PERSON" in recognizer.supported_entities
    assert "LOCATION" in recognizer.supported_entities
    assert "ORGANIZATION" in recognizer.supported_entities


def test_load_requires_model_name():
    """Test that load() raises error if model_name not set."""
    # Patch hf_pipeline to avoid ImportError if transformers is missing in env
    with patch(HF_PIPELINE_PATH, return_value=MagicMock()):
        # ValueError is raised during __init__ because EntityRecognizer calls load()
        with pytest.raises(ValueError, match="model_name must be set"):
            HuggingFaceNerRecognizer()  # No model_name


def test_load_invokes_hf_pipeline_with_expected_args():
    """Test that load() calls hf_pipeline with correct arguments."""
    with patch(HF_PIPELINE_PATH) as mock_hf_pipeline:
        recognizer = HuggingFaceNerRecognizer(
            model_name="test-model",
            aggregation_strategy="simple",
            device=-1  # Explicitly set device to ensure deterministic test
        )
        recognizer.load()

        mock_hf_pipeline.assert_called_once_with(
            "token-classification",
            model="test-model",
            tokenizer="test-model",
            aggregation_strategy="simple",
            device=-1
        )


def test_split_text_to_char_chunks():
    """Test text splitting logic."""
    # text length 100, chunk 50, overlap 10
    chunks = HuggingFaceNerRecognizer.split_text_to_char_chunks(100, 50, 10)

    assert len(chunks) == 3
    assert chunks[0] == [0, 50]
    assert chunks[1] == [40, 90]
    assert chunks[2] == [80, 100]


def test_analyze_long_text_chunking(mock_transformers_pipeline):
    """Test that long text is split into chunks and offsets are corrected."""
    text = "0123456789" * 4  # 40 chars

    # Force chunking by setting small chunk_size
    # Chunk size 20, overlap 10 -> step 10
    # Chunks: [0, 20], [10, 30], [20, 40]
    recognizer = HuggingFaceNerRecognizer(
        model_name="test",
        chunk_size=20,
        chunk_overlap_size=10
    )
    recognizer.ner_pipeline = mock_transformers_pipeline

    # Mock return values for BATCH processing (list of lists)
    # The pipeline is called ONCE with a list of 3 strings.
    # Chunk 1 (0-20): Find 'A' at 5-6 -> global 5-6
    # Chunk 2 (10-30): Find 'B' at 5-6 (local) -> 10+5=15 -> global 15-16
    # Chunk 3 (20-40): No entities
    mock_transformers_pipeline.return_value = [
        [{"entity_group": "PER", "start": 5, "end": 6, "score": 0.9}],
        [{"entity_group": "LOC", "start": 5, "end": 6, "score": 0.9}],
        [],
    ]

    results = recognizer.analyze(text, ["PERSON", "LOCATION"])

    # Sort results by start index for stable assertions
    results.sort(key=lambda x: x.start)

    # Should find 2 entities
    assert len(results) == 2

    # First entity: PERSON at 5-6
    assert results[0].entity_type == "PERSON"
    assert results[0].start == 5
    assert results[0].end == 6

    # Second entity: LOCATION at 15-16
    assert results[1].entity_type == "LOCATION"
    assert results[1].start == 15
    assert results[1].end == 16


def test_analyze_deduplication_keeps_highest_score(mock_transformers_pipeline):
    """Test deduplication keeps highest score when same span detected twice."""
    # Scenario: Chunking creates two detections for the same entity span
    # One has low score (0.6), one has high score (0.95)
    mock_transformers_pipeline.return_value = [
        # Chunk 1 (0~20): Detects "A...A" at global 16~18 (Local 16~18)
        [{"entity_group": "PER", "start": 16, "end": 18, "score": 0.60}],
        # Chunk 2 (15~35): Detects "A...A" at global 16~18
        # Since chunk_start is 15, Global 16~18 maps to Local 1~3 (16-15=1, 18-15=3)
        [{"entity_group": "PER", "start": 1, "end": 3, "score": 0.95}],
        # Chunk 3 (30~50): No entities
        []
    ]

    recognizer = HuggingFaceNerRecognizer(
        model_name="test-model",
        chunk_size=20,     # Small chunk size to force chunking
        chunk_overlap_size=5
    )
    recognizer.ner_pipeline = mock_transformers_pipeline

    text = "A" * 50  # Dummy text
    results = recognizer.analyze(text, ["PERSON"])

    # Sort results by start index for stable assertions
    results.sort(key=lambda x: x.start)

    # Should be deduplicated to 1 result
    assert len(results) == 1
    # Highest score should be kept
    assert results[0].score == pytest.approx(0.95, rel=1e-2)


def test_analyze_text_too_long(mock_transformers_pipeline):
    """Test that text is truncated when exceeding max_text_length."""
    text = "1234567890"  # 10 chars

    # Set max length to 5
    recognizer = HuggingFaceNerRecognizer(
        model_name="test",
        max_text_length=5
    )
    recognizer.ner_pipeline = mock_transformers_pipeline

    # Mock return for the truncated text "12345"
    mock_transformers_pipeline.return_value = [
        [{"entity_group": "PER", "start": 0, "end": 2, "score": 0.9}]
    ]

    recognizer.analyze(text, ["PERSON"])

    # Verify the first positional arg is a list of strings for batching
    args, _ = mock_transformers_pipeline.call_args
    assert args[0] == ["12345"]


def test_analyze_batch_processing_fallback(mock_transformers_pipeline):
    """Test fallback to iterative processing when batching fails."""
    # Scenario: Batch processing raises RuntimeError -> Iterative calls match
    # Text length 20, chunk size 10 -> 2 chunks (if overlap=0)

    # Side effects:
    # 1. Batch call (list input): Raises RuntimeError
    # 2. Iterative call 1 (str input): Returns result
    # 3. Iterative call 2 (str input): Returns empty
    mock_transformers_pipeline.side_effect = [
        RuntimeError("Batching failed"),
        [{"entity_group": "PER", "start": 0, "end": 5, "score": 0.9}],
        []
    ]

    recognizer = HuggingFaceNerRecognizer(
        model_name="test",
        chunk_size=10,
        chunk_overlap_size=0,
        batch_size=2
    )
    recognizer.ner_pipeline = mock_transformers_pipeline

    text = "12345678901234567890" # 20 chars
    results = recognizer.analyze(text, ["PERSON"])

    # Fallback should succeed and find entity from first chunk
    assert len(results) == 1
    assert results[0].entity_type == "PERSON"

    # Must have called pipeline at least twice (1 failed batch + 2 iterative)
    assert mock_transformers_pipeline.call_count >= 2

