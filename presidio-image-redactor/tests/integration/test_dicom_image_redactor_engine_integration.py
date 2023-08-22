"""Integration test for the DicomImageRedactorEngine class

Note that we are not asserting every pixel is equal when comparing original to redacted images
to account for differences in performance with different versions of Tesseract OCR.
"""
import tempfile
import pydicom
from pathlib import Path
import os
import numpy as np
from presidio_image_redactor.dicom_image_redactor_engine import DicomImageRedactorEngine
import pytest

SCRIPT_DIR = os.path.dirname(__file__)
RESOURCES_PARENT_DIR = f"{SCRIPT_DIR}/resources"
RESOURCES_DIR1 = f"{SCRIPT_DIR}/resources/dir1"
RESOURCES_DIR2 = f"{SCRIPT_DIR}/resources/dir1/dir2"


@pytest.fixture(scope="module")
def mock_engine():
    """Instance of the DicomImageRedactorEngine"""
    dicom_image_redactor_engine = DicomImageRedactorEngine()

    return dicom_image_redactor_engine


@pytest.mark.parametrize(
    "dcm_filepath",
    [
        (Path(RESOURCES_PARENT_DIR, "0_ORIGINAL.dcm")),
        (Path(RESOURCES_DIR2, "1_ORIGINAL.dcm")),
        (Path(RESOURCES_DIR2, "2_ORIGINAL.dcm")),
    ],
)
def test_redact_image_correctly(
    mock_engine: DicomImageRedactorEngine, dcm_filepath: Path
):
    """Test the redact function

    Args:
        mock_engine (DicomImageRedactorEngine): Mock instance.
        dcm_filepath (Path): Path to DICOM file to load.
    """
    test_image = pydicom.dcmread(dcm_filepath)
    test_redacted_image = mock_engine.redact(test_image, use_metadata=True)

    assert (
        np.array_equal(test_image.pixel_array, test_redacted_image.pixel_array) is False
    )


def test_redact_from_single_file_correctly(mock_engine: DicomImageRedactorEngine):
    """Test the redact_from_file function with single file case

    Args:
        mock_engine (DicomImageRedactorEngine): Mock instance.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Set file paths and redact PII
        input_path = Path(RESOURCES_PARENT_DIR, "0_ORIGINAL.dcm")
        mock_engine.redact_from_file(
            input_dicom_path=str(input_path),
            output_dir=tmpdirname,
            fill="contrast",
            use_metadata=True
        )
        output_path = Path(tmpdirname, f"{input_path.stem}.dcm")

        # Load original and redacted files
        instance_original = pydicom.dcmread(str(input_path))
        instance_redacted = pydicom.dcmread(str(output_path))

    # Compare original to redacted file
    original_pixels = instance_original[0x7FE0, 0x0010]
    redacted_pixels = instance_redacted[0x7FE0, 0x0010]
    same_elements = []

    for element in instance_original:
        # Get the element tag
        tag = element.tag

        # Check the same element for both instances
        element_original = instance_original[tag]
        element_redacted = instance_redacted[tag]

        if element_original == element_redacted:
            same_elements.append(tag)

    assert len(instance_original) - 1 == len(
        same_elements
    )  # only PixelData should be different
    assert original_pixels != redacted_pixels


def test_redact_from_directory_correctly(mock_engine: DicomImageRedactorEngine):
    """Test the redact_from_file function with multiple files case

    Args:
        mock_engine (DicomImageRedactorEngine): Mock instance.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Set file paths and redact PII
        input_path = Path(RESOURCES_DIR1)
        mock_engine.redact_from_directory(
            input_dicom_path=str(input_path),
            output_dir=tmpdirname,
            fill="contrast",
            use_metadata=True
        )

        # Get list of all DICOM files
        extensions = ["[dD][cC][mM]", "[dD][iI][cC][oO][mM]"]
        input_files = []
        for extension in extensions:
            p = input_path.glob(f"**/*.{extension}")
            files = [x for x in p if x.is_file()]
            input_files += files

        output_files = []
        for extension in extensions:
            p = Path(tmpdirname).glob(f"**/*.{extension}")
            files = [x for x in p if x.is_file()]
            output_files += files

    assert len(output_files) == len(input_files)
