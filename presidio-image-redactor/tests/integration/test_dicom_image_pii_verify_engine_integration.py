"""Integration test for dicom_image_pii_verify_engine

Note we are not checking exact pixel data for the returned image
because that is covered by testing of the "verify" function in
the original parent ImagePiiVerifyEngine class.
"""
import PIL
import pydicom
from copy import deepcopy
import pytest

from presidio_image_redactor import DicomImagePiiVerifyEngine, BboxProcessor

PADDING_WIDTH = 25

@pytest.fixture(scope="module")
def mock_instance(get_mock_dicom_instance: pydicom.dataset.FileDataset):
    return deepcopy(get_mock_dicom_instance)

@pytest.fixture(scope="module")
def mock_verify_results(get_mock_dicom_verify_results: dict):
    return deepcopy(get_mock_dicom_verify_results)

def _strip_score(analyzer_results_to_remove_score_from):
    [result.pop('score') for result in analyzer_results_to_remove_score_from]

def _set_of_tuples(list_of_dict):
    return set(frozenset(d.items()) for d in list_of_dict)


def test_verify_correctly(
    mock_instance: pydicom.dataset.FileDataset,
    mock_verify_results: dict,
):
    """Test the verify_dicom_instance function.

    Args:
        mock_instance (pydicom.dataset.FileDataset): Loaded DICOM.
        mock_verify_results (dict): Dictionary with loaded results.
    """
    # Assign
    expected_analyzer_results = deepcopy(mock_verify_results["analyzer_results"])
    expected_ocr_results_labels = []
    for item in mock_verify_results["ocr_results_formatted"]:
        expected_ocr_results_labels.append(item["label"])

    # Act
    test_image_verify, test_ocr_results, test_analyzer_results = DicomImagePiiVerifyEngine().verify_dicom_instance(
        instance=mock_instance,
        padding_width=PADDING_WIDTH,
        display_image=True,
        ocr_kwargs=None
    )

    # Assert
    assert type(test_image_verify) == PIL.Image.Image
    assert type(test_ocr_results) != None
    assert type(test_analyzer_results) != None

def test_eval_dicom_correctly(
    mock_instance: pydicom.dataset.FileDataset,
    mock_verify_results: dict,
):
    """Test the eval_dicom_instance function

    Args:
        mock_instance (pydicom.dataset.FileDataset): Loaded DICOM.
        mock_verify_results (dict): Dictionary with loaded results.
    """
    # Assign
    test_tolerance = 50
    test_ground_truth = deepcopy(mock_verify_results["ground_truth"])

    # Act
    test_image_eval, test_eval_results = DicomImagePiiVerifyEngine().eval_dicom_instance(
        instance = mock_instance,
        ground_truth = test_ground_truth,
        padding_width = PADDING_WIDTH,
        tolerance = test_tolerance,
        display_image = True,
        ocr_kwargs = None
    )

    # Assert
    assert type(test_image_eval) == PIL.Image.Image
    assert type(test_eval_results) != None
