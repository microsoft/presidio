"""Integration test for dicom_image_pii_verify_engine

Note we are not checking exact pixel data for the returned image
because that is covered by testing of the "verify" function in
the original parent ImagePiiVerifyEngine class.
"""
import PIL
import pydicom
from copy import deepcopy

from presidio_image_redactor import DicomImagePiiVerifyEngine, BboxProcessor
import pytest

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
    test_instance = deepcopy(get_mock_dicom_instance)
    bbox_processor = BboxProcessor()
    expected_ocr_results = deepcopy(get_mock_dicom_verify_results["ocr_results_formatted"])
    expected_analyzer_results = deepcopy(get_mock_dicom_verify_results["analyzer_results"])
    expected_ocr_results_labels = []
    for item in expected_ocr_results:
        expected_ocr_results_labels.append(item["label"])

    # Act
    (
        test_image,
        test_ocr_results,
        test_analyzer_results,
    ) = DicomImagePiiVerifyEngine().verify_dicom_instance(test_instance, PADDING_WIDTH)
    test_ocr_results_formatted = bbox_processor.get_bboxes_from_ocr_results(
        test_ocr_results
    )
    test_analyzer_results_formatted = bbox_processor.get_bboxes_from_analyzer_results(
        test_analyzer_results
    )

    # Check most OCR results (labels) are the same
    # Don't worry about position since that is implied in analyzer results
    test_ocr_results_labels = []
    for item in test_ocr_results_formatted:
        test_ocr_results_labels.append(item["label"])
    common_labels = set(expected_ocr_results_labels).intersection(
        set(test_ocr_results_labels)
    )
    all_labels = set(expected_ocr_results_labels).union(set(test_ocr_results_labels))

    # Assert
    assert type(test_image) == PIL.Image.Image
    assert len(common_labels) / len(all_labels) >= 0.5
    _strip_score(expected_analyzer_results)
    _strip_score(test_analyzer_results_formatted)
    assert all([result in expected_analyzer_results for result in test_analyzer_results_formatted])

def test_eval_dicom_correctly(
    mocker,
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

    # TODO: Delete after temporary testing
    ocr_results_raw = {
        "level": [
            1,
            2,
            3,
            4,
            5,
            5,
            5,
            5,
            4,
            5,
            5,
            2,
            3,
            4,
            5,
            5,
            2,
            3,
            4,
            5,
            2,
            3,
            4,
            5
        ],
        "page_num": [
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1
        ],
        "block_num": [
            0,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            2,
            2,
            2,
            2,
            2,
            3,
            3,
            3,
            3,
            4,
            4,
            4,
            4
        ],
        "par_num": [
            0,
            0,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            0,
            1,
            1,
            1,
            1,
            0,
            1,
            1,
            1,
            0,
            1,
            1,
            1
        ],
        "line_num": [
            0,
            0,
            0,
            1,
            1,
            1,
            1,
            1,
            2,
            2,
            2,
            0,
            0,
            1,
            1,
            1,
            0,
            0,
            1,
            1,
            0,
            0,
            1,
            1
        ],
        "word_num": [
            0,
            0,
            0,
            0,
            1,
            2,
            3,
            4,
            0,
            1,
            2,
            0,
            0,
            0,
            1,
            2,
            0,
            0,
            0,
            1,
            0,
            0,
            0,
            1
        ],
        "left": [
            0,
            25,
            25,
            25,
            25,
            287,
            535,
            613,
            42,
            42,
            170,
            1774,
            1774,
            1774,
            1774,
            2151,
            1920,
            1920,
            1920,
            1920,
            0,
            0,
            0,
            0
        ],
        "top": [
            0,
            25,
            25,
            25,
            25,
            25,
            25,
            26,
            70,
            70,
            72,
            25,
            25,
            25,
            40,
            25,
            128,
            128,
            128,
            128,
            0,
            0,
            0,
            0
        ],
        "width": [
            2190,
            814,
            814,
            814,
            241,
            230,
            60,
            226,
            346,
            110,
            218,
            391,
            391,
            391,
            343,
            14,
            221,
            221,
            221,
            221,
            2190,
            2190,
            2190,
            2190
        ],
        "height": [
            1810,
            82,
            82,
            45,
            37,
            36,
            45,
            35,
            37,
            37,
            35,
            69,
            69,
            69,
            54,
            12,
            36,
            36,
            36,
            36,
            1810,
            1810,
            1810,
            1810
        ],
        "conf": [
            "-1",
            "-1",
            "-1",
            "-1",
            "95.833916",
            "93.292221",
            "92.131226",
            "96.588577",
            "-1",
            "95.489471",
            "95.489471",
            "-1",
            "-1",
            "-1",
            "91.714470",
            "11.772476",
            "-1",
            "-1",
            "-1",
            "96.337395",
            "-1",
            "-1",
            "-1",
            "95.000000"
        ],
        "text": [
            "",
            "",
            "",
            "",
            "DAVIDSON",
            "DOUGLAS",
            "[M]",
            "01.09.2012",
            "",
            "DOB:",
            "06.16.1976",
            "",
            "",
            "",
            "Semi-Upright",
            ":",
            "",
            "",
            "",
            "Portable",
            "",
            "",
            "",
            ""
        ]
    }
    test_analyzer_results = [
        {
            "entity_type": "PERSON",
            "score": 1.0,
            "left": 25,
            "top": 25,
            "width": 241,
            "height": 37
        },
        {
            "entity_type": "PERSON",
            "height": 36,
            "left": 287,
            "score": 1,
            "top": 25,
            "width": 230
        },
        {
            "entity_type": "PERSON",
            "score": 0.85,
            "left": 287,
            "top": 25,
            "width": 230,
            "height": 36
        },
        {
            "entity_type": "PERSON",
            "score": 1.0,
            "left": 535,
            "top": 25,
            "width": 60,
            "height": 45
        },
        {
            "entity_type": "DATE_TIME",
            "score": 0.6,
            "left": 613,
            "top": 26,
            "width": 226,
            "height": 35
        },
        {
            "entity_type": "PERSON",
            "score": 1.0,
            "left": 170,
            "top": 72,
            "width": 218,
            "height": 35
        },
        {
            "entity_type": "PHONE_NUMBER",
            "score": 0.4,
            "left": 170,
            "top": 72,
            "width": 218,
            "height": 35
        }
    ]
    mocker.patch.object(
        DicomImagePiiVerifyEngine,
        "verify_dicom_instance",
        return_value=[PIL.Image.Image(), ocr_results_raw, test_analyzer_results],
    )
    mocker.patch(
        "presidio_image_redactor.dicom_image_pii_verify_engine.BboxProcessor.get_bboxes_from_analyzer_results",
        return_value=test_analyzer_results,
    )
    mocker.patch.object(
        DicomImagePiiVerifyEngine,
        "_remove_duplicate_entities",
        return_value=None,
    )
    mocker.patch.object(
        DicomImagePiiVerifyEngine,
        "_label_all_positives",
        return_value=test_all_pos,
    )
    mocker.patch.object(
        DicomImagePiiVerifyEngine,
        "calculate_precision",
        return_value=1.0,
    )
    mocker.patch.object(
        DicomImagePiiVerifyEngine,
        "calculate_recall",
        return_value=1.0,
    )

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
    # _strip_score(test_eval_results['all_positives'])
    _strip_score(expected_results['all_positives'])
    assert test_eval_results == expected_results

def _strip_score(analyzer_results):
    [result.pop('score') for result in analyzer_results]
