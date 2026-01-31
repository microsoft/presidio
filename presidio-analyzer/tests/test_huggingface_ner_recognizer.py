"""Tests for HuggingFaceNerRecognizer."""

import logging
from unittest.mock import MagicMock, mock_open, patch

import pytest
from presidio_analyzer.predefined_recognizers import HuggingFaceNerRecognizer
from presidio_analyzer.recognizer_registry.recognizers_loader_utils import (
    RecognizerConfigurationLoader,
    RecognizerListLoader,
)

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
    mock_transformers_pipeline.return_value = [[], []] # Empty for any chunks calls

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
        HuggingFaceNerRecognizer(
            model_name="test-model",
            aggregation_strategy="simple",
            device=-1  # Explicitly set device to ensure deterministic test
        )

        mock_hf_pipeline.assert_called_once_with(
            "token-classification",
            model="test-model",
            tokenizer="test-model",
            aggregation_strategy="simple",
            device=-1
        )





def test_analyze_long_text_chunking(mock_transformers_pipeline):
    """Test that long text is split into chunks and offsets are corrected."""
    # Use text with spaces for predictable boundaries
    # Text: "A A A A A A A A A A..." (Indices: 0, 2, 4, 6, 8...)
    text = ("A " * 20).strip() # Length 39

    recognizer = HuggingFaceNerRecognizer(
        model_name="test",
        chunk_size=10,
        chunk_overlap=4
    )
    # The CharacterBasedTextChunker is initialized inside the recognizer
    # using these parameters.
    recognizer.ner_pipeline = mock_transformers_pipeline

    # Chunk 1: "A A A A A " (0-10). Extends to 11 (space at 11 is boundary).
    # Range 0-11.
    # Mock Entity: PER at 2-3 ("A"). Global 2-3.

    # Next start: 11 - 4 = 7.
    # Chunk 2 Start 7.
    # Text[7] is ' '. Text[8] is 'A'.
    # Mock Entity: LOC at 8-9 (Global).
    # Relative start for Global 8: 8 - 7 = 1.
    # Relative end for Global 9: 9 - 7 = 2.

    mock_transformers_pipeline.side_effect = [
        [{"entity_group": "PER", "start": 2, "end": 3, "score": 0.9}],
        [{"entity_group": "LOC", "start": 1, "end": 2, "score": 0.9}],
        [], [], [], [], [], [], [], [], [], [] # Extended returns
    ]

    results = recognizer.analyze(text, ["PERSON", "LOCATION"])
    results.sort(key=lambda x: x.start)

    assert len(results) == 2

    # First entity: PERSON at 2-3
    assert results[0].entity_type == "PERSON"
    assert results[0].start == 2
    assert results[0].end == 3

    # Second entity: LOCATION at 8-9
    assert results[1].entity_type == "LOCATION"
    assert results[1].start == 8
    assert results[1].end == 9


def test_analyze_deduplication_keeps_highest_score(mock_transformers_pipeline):
    """Test deduplication keeps highest score when same span detected twice."""
    text = ("A " * 20).strip()

    recognizer = HuggingFaceNerRecognizer(
        model_name="test-model",
        chunk_size=10,
        chunk_overlap=8  # Start 11-8=3 to overlap Global 4-5
    )
    recognizer.ner_pipeline = mock_transformers_pipeline

    # Chunk 1: 0-11.
    #   Mock: PER at 4-5 (Global 4-5). Score 0.6.

    # Next start: 11 - 8 = 3.
    # Chunk 2 Start 3.
    #   Mock: PER at Global 4-5.
    #   Relative start: 4 - 3 = 1.
    #   Relative end: 5 - 3 = 2.

    mock_transformers_pipeline.side_effect = [
        [{"entity_group": "PER", "start": 4, "end": 5, "score": 0.60}],
        [{"entity_group": "PER", "start": 1, "end": 2, "score": 0.95}],
        [], [], [], [], [], [], [], [], [], []
    ]

    results = recognizer.analyze(text, ["PERSON"])
    results.sort(key=lambda x: x.start)

    assert len(results) == 1
    assert results[0].score == pytest.approx(0.95, rel=1e-2)
    assert results[0].start == 4
    assert results[0].end == 5


def test_analyze_text_too_long(mock_transformers_pipeline):
    """Test that text is truncated when exceeding max_text_length."""
    text = "1234567890"  # 10 chars

    # Set max length to 5
    recognizer = HuggingFaceNerRecognizer(model_name="test", max_text_length=5)
    recognizer.ner_pipeline = mock_transformers_pipeline

    # Mock return for the truncated text "12345"
    mock_transformers_pipeline.return_value = [
        [{"entity_group": "PER", "start": 0, "end": 2, "score": 0.9}]
    ]

    recognizer.analyze(text, ["PERSON"])

    # Verify the first positional arg is the string (not list, since iterative)
    args, _ = mock_transformers_pipeline.call_args
    # It should be called with the truncated string
    assert args[0] == "12345"


def test_hf_recognizer_init_variations(caplog):
    """Test various initialization scenarios and warnings."""
    caplog.set_level(logging.WARNING)
    path = HF_PIPELINE_PATH
    with patch(path, new=MagicMock()):
        # Check warning for aggregation_strategy='none'
        HuggingFaceNerRecognizer(model_name="test", aggregation_strategy="none")
        assert (
            "aggregation_strategy='none' may result in fragmented entities"
            in caplog.text
        )

        # Verify supported_entities is correctly stored in the base class field
        rec2 = HuggingFaceNerRecognizer(
            model_name="test", supported_entities=["TEST_ENTITY"]
        )
        assert "TEST_ENTITY" in rec2.supported_entities


def test_hf_recognizer_load_errors():
    """Test error handling during model loading phase."""
    path = HF_PIPELINE_PATH
    # 1. Test ImportError when transformers is missing
    with patch(path, new=None):
        with pytest.raises(ImportError):
            HuggingFaceNerRecognizer(model_name="test")

    # 2. Test ValueError when model_name is missing
    with patch(path, new=MagicMock()):
        with pytest.raises(ValueError, match="model_name must be set"):
            HuggingFaceNerRecognizer(model_name=None)


def test_hf_recognizer_analyze_truncation_and_lazy_load(caplog):
    """Test text truncation logic and automatic lazy loading in analyze()."""
    caplog.set_level(logging.WARNING)
    path = HF_PIPELINE_PATH
    with patch(path, new=MagicMock()):
        rec = HuggingFaceNerRecognizer(model_name="test", max_text_length=5)

        # Stub predict_with_chunking to avoid calling the real internal predict_func
        rec.text_chunker = MagicMock()
        rec.text_chunker.predict_with_chunking.side_effect = lambda **kwargs: []

        rec.ner_pipeline = None

        with patch.object(rec, "load") as mock_load:
            rec.analyze("123456", entities=[])  # Input longer than max_text_length

            # Verify automatic load was triggered
            mock_load.assert_called_once()
            # Verify truncation warning was logged
            assert "exceeds max_text_length" in caplog.text
            # Verify call_args to ensure text was actually truncated to 5 chars
            assert rec.text_chunker.predict_with_chunking.called
            called_kwargs = rec.text_chunker.predict_with_chunking.call_args.kwargs
            assert called_kwargs["text"] == "12345"


@pytest.mark.parametrize(
    "device_input, expected_device",
    [
        ("cpu", -1),
        ("cuda", 0),
        ("cuda:1", 1),
        (0, 0),
    ],
)
def test_hf_recognizer_device_parsing(device_input, expected_device):
    """Test that various device strings/ints are correctly parsed for the pipeline."""
    path = HF_PIPELINE_PATH
    with patch(path) as mock_pipeline:
        HuggingFaceNerRecognizer(model_name="test", device=device_input)
        # Ensure it was called exactly once with expected device
        mock_pipeline.assert_called_once()
        _, kwargs = mock_pipeline.call_args
        assert kwargs["device"] == expected_device


def test_hf_recognizer_prediction_edge_cases(caplog):
    """Test prediction callback with various model output formats."""
    caplog.set_level(logging.WARNING)
    path = HF_PIPELINE_PATH
    # Inject explicit label_mapping and threshold to avoid dependency on global defaults
    test_mapping = {"PER": "TEST_PERSON"}
    with patch(path, new=MagicMock()):
        rec = HuggingFaceNerRecognizer(
            model_name="test",
            label_mapping=test_mapping,
            threshold=0.0,
        )

    rec.ner_pipeline = MagicMock()

    # Case 1: Model returns a label not in mapping (entity key)
    rec.ner_pipeline.return_value = [
        {"entity": "UNKNOWN", "score": 0.9, "start": 0, "end": 4}
    ]
    assert len(rec._predict_chunk("text")) == 0

    # Case 2: Model returns BIO-prefixed label (B-PER -> mapped to TEST_PERSON)
    rec.ner_pipeline.return_value = [
        {"entity_group": "B-PER", "score": 0.9, "start": 0, "end": 4}
    ]
    results = rec._predict_chunk("text")
    assert len(results) == 1
    assert results[0].entity_type == "TEST_PERSON"

    # Case 3: Inference engine throws an exception
    rec.ner_pipeline.side_effect = Exception("Pipeline failure")
    assert rec._predict_chunk("text") == []
    assert "NER prediction failed" in caplog.text


def test_prepare_recognizer_kwargs_exception(caplog):
    """Test fallback logic when inspect.signature fails."""
    caplog.set_level(logging.WARNING)

    class DummyRec:
        pass

    # Patch inspect.signature relative to the utility module
    target = (
        "presidio_analyzer.recognizer_registry."
        "recognizers_loader_utils.inspect.signature"
    )
    with patch(target, side_effect=Exception("Inspection failed")):
        kwargs = RecognizerListLoader._prepare_recognizer_kwargs(
            {"p1": "v1"}, {"p2": "v2"}, DummyRec
        )
        # Verify warning log and fallback to basic merge
        assert "Failed to inspect signature" in caplog.text
        assert kwargs == {"p1": "v1", "p2": "v2"}


def test_get_config_yaml_error():
    """Test error wrapping when YAML parsing fails in ConfigurationLoader."""
    # Patch safe_load relative to the utility module
    yaml_patch = (
        "presidio_analyzer.recognizer_registry.recognizers_loader_utils.yaml.safe_load"
    )
    with patch("builtins.open", mock_open(read_data="dummy: content")):
        with patch(yaml_patch, side_effect=Exception("YAML Parse Error")):
            with pytest.raises(ValueError, match="Failed to parse file"):
                RecognizerConfigurationLoader.get(conf_file="invalid.yaml")
