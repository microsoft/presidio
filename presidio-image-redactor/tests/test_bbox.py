"""Test suite for bbox.py"""
from presidio_image_redactor import BboxProcessor
from presidio_image_redactor.entities.image_recognizer_result import (
    ImageRecognizerResult,
)
import pytest

from typing import List


@pytest.fixture(scope="module")
def mock_bbox_processor():
    """Instance of BboxProcessor"""
    bbox_proc = BboxProcessor()

    return bbox_proc


# ------------------------------------------------------
# BboxProcessor.get_bboxes_from_ocr_results()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "ocr_results_raw, expected_results",
    [
        (
            {
                "left": [123],
                "top": [0],
                "width": [100],
                "height": [25],
                "conf": ["1"],
                "text": ["JOHN"],
            },
            [
                {
                    "left": 123,
                    "top": 0,
                    "width": 100,
                    "height": 25,
                    "conf": 1,
                    "label": "JOHN",
                }
            ],
        ),
        (
            {
                "left": [123, 345],
                "top": [0, 15],
                "width": [100, 75],
                "height": [25, 30],
                "conf": ["1", "0.87"],
                "text": ["JOHN", "DOE"],
            },
            [
                {
                    "left": 123,
                    "top": 0,
                    "width": 100,
                    "height": 25,
                    "conf": 1,
                    "label": "JOHN",
                },
                {
                    "left": 345,
                    "top": 15,
                    "width": 75,
                    "height": 30,
                    "conf": 0.87,
                    "label": "DOE",
                },
            ],
        ),
    ],
)
def test_get_bboxes_from_ocr_results_happy_path(
    mock_bbox_processor: BboxProcessor,
    ocr_results_raw: dict,
    expected_results: list,
):
    """Test happy path for BboxProcessor.get_bboxes_from_ocr_results
    Args:
        mock_bbox_processor (BboxProcessor): Instantiated engine.
        ocr_results_raw (dict): Raw OCR results.
        expected_results (list): Formatted OCR results.
    """
    # Act
    test_bboxes = mock_bbox_processor.get_bboxes_from_ocr_results(ocr_results_raw)

    # Assert
    assert test_bboxes == expected_results


# ------------------------------------------------------
# BboxProcessor.get_bboxes_from_analyzer_results()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "analyzer_results, expected_bboxes",
    [
        (
            [
                ImageRecognizerResult(
                    entity_type="TYPE_1",
                    start=0,
                    end=0,
                    left=25,
                    top=25,
                    width=100,
                    height=100,
                    score=0.99,
                ),
                ImageRecognizerResult(
                    entity_type="TYPE_2",
                    start=10,
                    end=10,
                    left=25,
                    top=49,
                    width=75,
                    height=51,
                    score=0.7,
                ),
                ImageRecognizerResult(
                    entity_type="TYPE_3",
                    start=25,
                    end=35,
                    left=613,
                    top=26,
                    width=226,
                    height=35,
                    score=0.6,
                ),
            ],
            [
                {
                    "entity_type": "TYPE_1",
                    "score": 0.99,
                    "left": 25,
                    "top": 25,
                    "width": 100,
                    "height": 100,
                },
                {
                    "entity_type": "TYPE_2",
                    "score": 0.7,
                    "left": 25,
                    "top": 49,
                    "width": 75,
                    "height": 51,
                },
                {
                    "entity_type": "TYPE_3",
                    "score": 0.6,
                    "left": 613,
                    "top": 26,
                    "width": 226,
                    "height": 35,
                },
            ],
        ),
    ],
)
def test_get_bboxes_from_analyzer_results_happy_path(
    mock_bbox_processor: BboxProcessor,
    analyzer_results: list,
    expected_bboxes: list,
):
    """Test happy path for BboxProcessor.get_bboxes_from_analyzer_results

    Args:
        analyzer_results (list): Results from using ImageAnalyzerEngine.
        expected_bboxes (list): Expected output bounding box list.
    """
    # Arrange

    # Act
    test_bboxes = mock_bbox_processor.get_bboxes_from_analyzer_results(analyzer_results)

    # Assert
    assert test_bboxes == expected_bboxes


# ------------------------------------------------------
# BboxProcessor.remove_bbox_padding()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "mock_intermediate_bbox, padding_width, expected_bboxes",
    [
        (
            [
                {
                    "entity_type": "TYPE_1",
                    "score": 0.99,
                    "left": 10,
                    "top": 15,
                    "width": 100,
                    "height": 100,
                },
                {
                    "entity_type": "TYPE_2",
                    "score": 0.7,
                    "left": 25,
                    "top": 49,
                    "width": 75,
                    "height": 51,
                },
                {
                    "entity_type": "TYPE_3",
                    "score": 0.6,
                    "left": 613,
                    "top": 26,
                    "width": 226,
                    "height": 35,
                },
            ],
            25,
            [
                {"top": 0, "left": 0, "width": 100, "height": 100},
                {"top": 24, "left": 0, "width": 75, "height": 51},
                {"top": 1, "left": 588, "width": 226, "height": 35},
            ],
        ),
    ],
)
def test_remove_bbox_padding_happy_path(
    mock_bbox_processor: BboxProcessor,
    mock_intermediate_bbox: dict,
    padding_width: int,
    expected_bboxes: list,
):
    """Test happy path for BboxProcessor.remove_bbox_padding

    Args:
        mock_intermediate_bbox (dict): Value for mock of get_bboxes_from_analyzer_results.
        padding_width (int): Pixel width used for padding.
        expected_bboxes_dict (dict): Expected output bounding box dictionary.
    """
    # Arrange

    # Act
    test_bboxes_dict = mock_bbox_processor.remove_bbox_padding(mock_intermediate_bbox, padding_width)

    # Assert
    assert test_bboxes_dict == expected_bboxes


@pytest.mark.parametrize(
    "padding_width, expected_error_type",
    [(-1, "ValueError"), (-200, "ValueError")],
)
def test_remove_bbox_padding_exceptions(
    mock_bbox_processor: BboxProcessor, padding_width: int, expected_error_type: str
):
    """Test error handling of remove_bbox_padding

    Args:
        padding_width (int): Pixel width used for padding.
        expected_error_type (str): Type of error we expect to be raised.
    """
    with pytest.raises(Exception) as exc_info:
        # Act
        _ = mock_bbox_processor.remove_bbox_padding([], padding_width)

    # Assert
    assert expected_error_type == exc_info.typename


# ------------------------------------------------------
# DicomImagePiiVerifyEngine._match_with_source()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "source_labels, results, tolerance, expected_results, expected_match_found",
    [
        (
            [
                {
                    "label": "DAVIDSON",
                    "left": 25,
                    "top": 25,
                    "width": 241,
                    "height": 37,
                },
                {
                    "label": "DOUGLAS",
                    "left": 287,
                    "top": 25,
                    "width": 230,
                    "height": 36,
                },
                {
                    "label": "[M]",
                    "left": 535,
                    "top": 25,
                    "width": 60,
                    "height": 45,
                },
            ],
            {
                "entity_type": "PERSON",
                "score": 1.0,
                "left": 287,
                "top": 25,
                "width": 230,
                "height": 36,
            },
            50,
            [
                {
                    "label": "DOUGLAS",
                    "score": 1.0,
                    "left": 287,
                    "top": 25,
                    "width": 230,
                    "height": 36,
                }
            ],
            True,
        ),
        (
            [
                {
                    "label": "DAVIDSON",
                    "left": 25,
                    "top": 25,
                    "width": 241,
                    "height": 37,
                },
                {
                    "label": "DOUGLAS",
                    "left": 287,
                    "top": 25,
                    "width": 230,
                    "height": 36,
                },
                {
                    "label": "[M]",
                    "left": 535,
                    "top": 25,
                    "width": 60,
                    "height": 45,
                },
            ],
            {
                "entity_type": "PERSON",
                "score": 1.0,
                "left": 300,
                "top": 15,
                "width": 250,
                "height": 40,
            },
            50,
            [
                {
                    "label": "DOUGLAS",
                    "score": 1.0,
                    "left": 287,
                    "top": 25,
                    "width": 230,
                    "height": 36,
                }
            ],
            True,
        ),
        (
            [
                {
                    "label": "DAVIDSON",
                    "left": 25,
                    "top": 25,
                    "width": 241,
                    "height": 37,
                },
                {
                    "label": "DOUGLAS",
                    "left": 287,
                    "top": 25,
                    "width": 230,
                    "height": 36,
                },
                {
                    "label": "[M]",
                    "left": 535,
                    "top": 25,
                    "width": 60,
                    "height": 45,
                },
            ],
            {
                "entity_type": "PERSON",
                "score": 1.0,
                "left": 99,
                "top": 99,
                "width": 99,
                "height": 99,
            },
            10,
            [],
            False,
        ),
    ],
)
def test_match_with_source_happy_path(
    mock_bbox_processor: BboxProcessor,
    source_labels: List[dict],
    results: dict,
    tolerance: int,
    expected_results: List[dict],
    expected_match_found: bool,
):
    """Test happy path for BboxProcessor.match_with_source

    Args:
        mock_bbox_processor (BboxProcessor): Instantiated engine.
        source_labels (dict): Ground truth labels for single instance.
        results (dict): Detected PHI dictionary.
        tolerance (int): Pixel difference tolerance for matching entities.
        expected_results (dict): Expected output dictionary.
        expected_match_found (bool): Expected match_found.
    """
    # Assign
    all_pos = []

    # Act
    test_all_pos, test_match_found = mock_bbox_processor.match_with_source(
        all_pos, source_labels, results, tolerance
    )

    # Assert
    assert test_all_pos == expected_results
    assert test_match_found == expected_match_found
