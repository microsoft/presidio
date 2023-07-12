"""Integration test for dicom_image_pii_verify_engine

Note we are not checking exact pixel data for the returned image
because that is covered by testing of the "verify" function in
the original parent ImagePiiVerifyEngine class.
"""
import PIL
import pydicom

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
    expected_ocr_results_labels = []
    for item in get_mock_dicom_verify_results["ocr_results_formatted"]:
        expected_ocr_results_labels.append(item["label"])

    # Act
    test_image_verify, test_ocr_results, _ = DicomImagePiiVerifyEngine().verify_dicom_instance(
        instance=get_mock_dicom_instance,
        padding_width=PADDING_WIDTH,
        display_image=True,
        ocr_kwargs=None
    )
    test_ocr_results_formatted = BboxProcessor().get_bboxes_from_ocr_results(
        ocr_results=test_ocr_results
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
