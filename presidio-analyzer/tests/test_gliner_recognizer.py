import sys

import pytest
from unittest.mock import MagicMock, patch

from presidio_analyzer.predefined_recognizers import GLiNERRecognizer


@pytest.fixture
def mock_gliner():
    """
    Fixture to mock GLiNER class and its methods.
    """

    pytest.importorskip("gliner", reason="GLiNER package is not installed")

    # Mock the GLiNER class and its methods
    mock_gliner_instance = MagicMock()
    # Mock the from_pretrained method to return the mock instance
    with patch("gliner.GLiNER.from_pretrained", return_value=mock_gliner_instance):
        yield mock_gliner_instance


def test_analyze_passed_entities_are_subset_of_entity_mapping(
    mock_gliner
):

    if sys.version_info < (3, 10):
        pytest.skip("gliner requires Python >= 3.10")

    # Mock GLiNER predict_entities
    mock_gliner.predict_entities.return_value = [
        {"label": "person", "start": 11, "end": 19, "score": 0.95},
        {"label": "location", "start": 33, "end": 41, "score": 0.85},
        {"label": "org", "start": 313, "end": 411, "score": 0.85},
    ]

    entity_mapping = {
        "person": "PERSON",
        "organization": "ORG",
        "location": "LOC",
    }

    gliner_recognizer = GLiNERRecognizer(
        entity_mapping=entity_mapping,
    )

    gliner_recognizer.gliner = mock_gliner
    text = "My name is John Doe from Seattle."
    entities = ["PERSON", "LOC"]

    results = gliner_recognizer.analyze(text, entities)

    # Check the number of results
    assert len(results) == 2

    # Check the first result
    assert results[0].entity_type == "PERSON"
    assert results[0].start == 11
    assert results[0].end == 19
    assert results[0].score == pytest.approx(0.95, rel=1e-2)

    # Check the second result
    assert results[1].entity_type == "LOC"
    assert results[1].start == 33
    assert results[1].end == 41
    assert results[1].score == pytest.approx(0.85, rel=1e-2)


def test_analyze_with_unsupported_entity(mock_gliner):


    if sys.version_info < (3, 10):
        pytest.skip("gliner requires Python >= 3.10")


    # Mock GLiNER predict_entities
    mock_gliner.gliner.predict_entities.return_value = [
        {"label": "BIRD", "start": 0, "end": 5, "score": 0.75},
    ]

    text = "Unknown entity."
    entities = ["PERSON", "LOC"]

    gliner_recognizer = GLiNERRecognizer(
        supported_entities=entities,
    )

    results = gliner_recognizer.analyze(text, entities)

    # Should filter out unsupported entities
    assert len(results) == 0


def test_analyze_with_entity_mapping(mock_gliner):
    # Mock GLiNER predict_entities
    mock_gliner.predict_entities.return_value = [
        {"label": "organization", "start": 10, "end": 20, "score": 0.90},
    ]

    text = "Works at Microsoft."
    entity_mapping = {"organization": "ORG"}

    gliner_recognizer = GLiNERRecognizer(
        entity_mapping=entity_mapping,
    )

    results = gliner_recognizer.analyze(text, ["ORG"])

    # Check mapping from 'organization' to 'ORG'
    assert len(results) == 1
    assert results[0].entity_type == "ORG"
    assert results[0].start == 10
    assert results[0].end == 20
    assert results[0].score == pytest.approx(0.90, rel=1e-2)


def test_analyze_with_no_entities(mock_gliner):
    # Mock GLiNER predict_entities
    mock_gliner.predict_entities.return_value = []

    text = "No entities here."
    entities = []


    gliner_recognizer = GLiNERRecognizer(
        supported_entities=["ORG", "LOC", "PER"],
    )

    results = gliner_recognizer.analyze(text, entities)

    # Should return no results
    assert len(results) == 0
