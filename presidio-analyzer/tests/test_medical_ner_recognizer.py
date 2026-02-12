import pytest
from unittest.mock import MagicMock, patch

from presidio_analyzer.predefined_recognizers import MedicalNERRecognizer
from presidio_analyzer.chunkers import CharacterBasedTextChunker


@pytest.fixture
def mock_pipeline():
    """Fixture to mock the HuggingFace token-classification pipeline."""
    mock_pipe = MagicMock()
    with patch(
        "presidio_analyzer.predefined_recognizers.ner"
        ".medical_ner_recognizer.hf_pipeline",
        return_value=mock_pipe,
    ):
        yield mock_pipe


def test_analyze_basic_entity_detection(mock_pipeline):
    """Test basic entity detection and mapping."""
    mock_pipeline.return_value = [
        {
            "entity_group": "DISEASE_DISORDER",
            "start": 24,
            "end": 32,
            "score": 0.95,
        },
        {
            "entity_group": "MEDICATION",
            "start": 53,
            "end": 63,
            "score": 0.90,
        },
    ]

    recognizer = MedicalNERRecognizer()
    recognizer.pipeline = mock_pipeline

    text = "The patient presents with diabetes and is prescribed metformin."
    entities = ["MEDICAL_DISEASE_DISORDER", "MEDICAL_MEDICATION"]
    results = recognizer.analyze(text, entities)

    assert len(results) == 2
    assert results[0].entity_type == "MEDICAL_DISEASE_DISORDER"
    assert results[0].start == 24
    assert results[0].end == 32
    assert results[0].score == pytest.approx(0.95, rel=1e-2)

    assert results[1].entity_type == "MEDICAL_MEDICATION"
    assert results[1].start == 53
    assert results[1].end == 63
    assert results[1].score == pytest.approx(0.90, rel=1e-2)


def test_analyze_filters_by_requested_entities(mock_pipeline):
    """Test that only requested entity types are returned."""
    mock_pipeline.return_value = [
        {
            "entity_group": "DISEASE_DISORDER",
            "start": 0,
            "end": 8,
            "score": 0.95,
        },
        {
            "entity_group": "MEDICATION",
            "start": 20,
            "end": 30,
            "score": 0.90,
        },
    ]

    recognizer = MedicalNERRecognizer()
    recognizer.pipeline = mock_pipeline

    text = "Diabetes treated with metformin."
    results = recognizer.analyze(text, ["MEDICAL_DISEASE_DISORDER"])

    assert len(results) == 1
    assert results[0].entity_type == "MEDICAL_DISEASE_DISORDER"


def test_analyze_score_threshold_filtering(mock_pipeline):
    """Test that predictions below score_threshold are filtered out."""
    mock_pipeline.return_value = [
        {
            "entity_group": "DISEASE_DISORDER",
            "start": 0,
            "end": 8,
            "score": 0.95,
        },
        {
            "entity_group": "MEDICATION",
            "start": 20,
            "end": 30,
            "score": 0.10,
        },
    ]

    recognizer = MedicalNERRecognizer(score_threshold=0.30)
    recognizer.pipeline = mock_pipeline

    text = "Diabetes treated with metformin."
    entities = ["MEDICAL_DISEASE_DISORDER", "MEDICAL_MEDICATION"]
    results = recognizer.analyze(text, entities)

    assert len(results) == 1
    assert results[0].entity_type == "MEDICAL_DISEASE_DISORDER"
    assert results[0].score == pytest.approx(0.95, rel=1e-2)


def test_analyze_custom_entity_mapping(mock_pipeline):
    """Test that a custom entity_mapping is used correctly."""
    mock_pipeline.return_value = [
        {
            "entity_group": "DISEASE_DISORDER",
            "start": 0,
            "end": 8,
            "score": 0.92,
        },
    ]

    custom_mapping = {"DISEASE_DISORDER": "CONDITION"}
    recognizer = MedicalNERRecognizer(entity_mapping=custom_mapping)
    recognizer.pipeline = mock_pipeline

    text = "Diabetes is common."
    results = recognizer.analyze(text, ["CONDITION"])

    assert len(results) == 1
    assert results[0].entity_type == "CONDITION"


def test_entity_mapping_and_supported_entities_conflict():
    """Test that providing both entity_mapping and supported_entities raises."""
    with pytest.raises(ValueError, match="cannot be used together"):
        MedicalNERRecognizer(
            entity_mapping={"DISEASE_DISORDER": "CONDITION"},
            supported_entities=["CONDITION"],
        )


def test_import_error_when_transformers_not_installed():
    """Test that load() raises ImportError when transformers is not installed."""
    with patch(
        "presidio_analyzer.predefined_recognizers.ner"
        ".medical_ner_recognizer.hf_pipeline",
        None,
    ):
        with pytest.raises(ImportError, match="transformers"):
            MedicalNERRecognizer()


def test_analyze_empty_predictions(mock_pipeline):
    """Test that empty pipeline output returns no results."""
    mock_pipeline.return_value = []

    recognizer = MedicalNERRecognizer()
    recognizer.pipeline = mock_pipeline

    text = "No medical entities here."
    entities = ["MEDICAL_DISEASE_DISORDER", "MEDICAL_MEDICATION"]
    results = recognizer.analyze(text, entities)

    assert len(results) == 0


def test_long_text_chunking_with_offset_verification(mock_pipeline):
    """Test that long text is chunked and offsets are adjusted correctly."""
    text = "Patient has diabetes. " + ("x " * 120) + "Prescribed metformin today."

    def mock_predict(text_chunk):
        entities = []
        if "diabetes" in text_chunk:
            start = text_chunk.find("diabetes")
            entities.append(
                {
                    "entity_group": "DISEASE_DISORDER",
                    "start": start,
                    "end": start + 8,
                    "score": 0.95,
                }
            )
        if "metformin" in text_chunk:
            start = text_chunk.find("metformin")
            entities.append(
                {
                    "entity_group": "MEDICATION",
                    "start": start,
                    "end": start + 9,
                    "score": 0.90,
                }
            )
        return entities

    mock_pipeline.side_effect = mock_predict

    recognizer = MedicalNERRecognizer(
        text_chunker=CharacterBasedTextChunker(chunk_size=250, chunk_overlap=50),
    )
    recognizer.pipeline = mock_pipeline

    entities = ["MEDICAL_DISEASE_DISORDER", "MEDICAL_MEDICATION"]
    results = recognizer.analyze(text, entities)

    assert mock_pipeline.call_count >= 2, "Should process multiple chunks"
    assert len(results) == 2

    assert text[results[0].start : results[0].end] == "diabetes"
    assert results[0].entity_type == "MEDICAL_DISEASE_DISORDER"

    assert text[results[1].start : results[1].end] == "metformin"
    assert results[1].entity_type == "MEDICAL_MEDICATION"


def test_supported_entities_without_mapping(mock_pipeline):
    """Test that supported_entities creates identity mapping when no mapping given."""
    mock_pipeline.return_value = [
        {
            "entity_group": "CUSTOM_ENTITY",
            "start": 0,
            "end": 5,
            "score": 0.80,
        },
    ]

    recognizer = MedicalNERRecognizer(
        supported_entities=["CUSTOM_ENTITY"],
    )
    recognizer.pipeline = mock_pipeline

    results = recognizer.analyze("Hello world.", ["CUSTOM_ENTITY"])

    assert len(results) == 1
    assert results[0].entity_type == "CUSTOM_ENTITY"


def test_default_entity_mapping_used(mock_pipeline):
    """Test that default mapping is used when no mapping or entities provided."""
    recognizer = MedicalNERRecognizer()

    expected_entities = {
        "MEDICAL_DISEASE_DISORDER",
        "MEDICAL_MEDICATION",
        "MEDICAL_THERAPEUTIC_PROCEDURE",
        "MEDICAL_CLINICAL_EVENT",
        "MEDICAL_BIOLOGICAL_ATTRIBUTE",
        "MEDICAL_BIOLOGICAL_STRUCTURE",
        "MEDICAL_FAMILY_HISTORY",
        "MEDICAL_HISTORY",
    }
    assert set(recognizer.supported_entities) == expected_entities
