"""Integration test for dicom_image_pii_verify_engine

Note we are not checking exact pixel data for the returned image
because that is covered by testing of the "verify" function in
the original parent ImagePiiVerifyEngine class.
"""
import PIL
import pydicom
from copy import deepcopy

from presidio_image_redactor import DicomImagePiiVerifyEngine, BboxProcessor

PADDING_WIDTH = 25

def test_verify_correctly(
    get_mock_dicom_instance: pydicom.dataset.FileDataset,
    get_mock_dicom_verify_results: dict,
):
    """Test the verify_dicom_instance function.

    Args:
        get_mock_dicom_instance (pydicom.dataset.FileDataset): Loaded DICOM.
        get_mock_dicom_verify_results (dict): Dictionary with loaded results.
    """
    # Assign
    test_instance_verify = deepcopy(get_mock_dicom_instance)
    expected_ocr_results = deepcopy(get_mock_dicom_verify_results["ocr_results_formatted"])
    expected_analyzer_results = deepcopy(get_mock_dicom_verify_results["analyzer_results"])
    expected_ocr_results_labels = []
    for item in expected_ocr_results:
        expected_ocr_results_labels.append(item["label"])

    # Act
    (
        test_image_verify,
        test_ocr_results,
        test_analyzer_results,
    ) = DicomImagePiiVerifyEngine().verify_dicom_instance(
        instance=test_instance_verify,
        padding_width=PADDING_WIDTH,
        display_image=True,
        ocr_kwargs=None
    )
    test_ocr_results_formatted = BboxProcessor().get_bboxes_from_ocr_results(
        ocr_results=test_ocr_results
    )
    test_analyzer_results_formatted = BboxProcessor().get_bboxes_from_analyzer_results(
        analyzer_results=test_analyzer_results
    )

    # Check most OCR results (labels) are the same
    # Don't worry about position since that is implied in analyzer results
    test_ocr_results_labels = []
    for item in test_ocr_results_formatted:
        test_ocr_results_labels.append(item["label"])
    test_common_labels = set(expected_ocr_results_labels).intersection(
        set(test_ocr_results_labels)
    )
    test_all_labels = set(expected_ocr_results_labels).union(set(test_ocr_results_labels))

    # Assert
    assert type(test_image_verify) == PIL.Image.Image
    assert len(test_common_labels) / len(test_all_labels) >= 0.5
    _strip_score(expected_analyzer_results)
    _strip_score(test_analyzer_results_formatted)
    assert all([result in expected_analyzer_results for result in test_analyzer_results_formatted])

def test_eval_dicom_correctly(
    get_mock_dicom_instance: pydicom.dataset.FileDataset,
    get_mock_dicom_verify_results: dict,
):
    """Test the eval_dicom_instance function

    Args:
        mock_engine (DicomImagePiiVerifyEngine): Instantiated engine.
        get_mock_dicom_instance (pydicom.dataset.FileDataset): Loaded DICOM.
        get_mock_dicom_verify_results (dict): Dictionary with loaded results.
    """
    # Assign
    test_instance = deepcopy(get_mock_dicom_instance)
    test_tolerance = 50
    test_ground_truth = deepcopy(get_mock_dicom_verify_results["ground_truth"])
    test_all_pos = deepcopy(get_mock_dicom_verify_results["all_pos"])
    expected_results = {
        "all_positives": test_all_pos,
        "ground_truth": test_ground_truth,
        "precision": 1.0,
        "recall": 1.0,
    }

    # Act
    test_image, test_eval_results = DicomImagePiiVerifyEngine().eval_dicom_instance(
        instance = test_instance,
        ground_truth = test_ground_truth,
        padding_width = PADDING_WIDTH,
        tolerance = test_tolerance,
        display_image = True,
        ocr_kwargs = None
    )

    # Assert
    assert type(test_image) == PIL.Image.Image
    _strip_score(test_eval_results['all_positives'])
    _strip_score(expected_results['all_positives'])
    assert test_eval_results == expected_results

def _strip_score(analyzer_results):
    [result.pop('score') for result in analyzer_results]
