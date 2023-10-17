"""Integration test for the DicomImageRedactorEngine class.

Note that we are not asserting every pixel is equal when comparing original to redacted
images to account for differences in performance with different versions of
OCR.
"""
import tempfile
import pydicom
from pathlib import Path
import os
import numpy as np

from typing import Callable

from tests.engine_test_utils import must_succeed, allow_failure
from presidio_image_redactor.dicom_image_redactor_engine import DicomImageRedactorEngine
from presidio_image_redactor.document_intelligence_ocr import DocumentIntelligenceOCR
from presidio_image_redactor.image_analyzer_engine import ImageAnalyzerEngine
import pytest

SCRIPT_DIR = os.path.dirname(__file__)
RESOURCES_PARENT_DIR = f"{SCRIPT_DIR}/resources"
RESOURCES_DIR1 = f"{SCRIPT_DIR}/resources/dir1"
RESOURCES_DIR2 = f"{SCRIPT_DIR}/resources/dir1/dir2"


@pytest.fixture
def mock_engine():
    """Instance of the DicomImageRedactorEngine."""
    dicom_image_redactor_engine = DicomImageRedactorEngine()
    return dicom_image_redactor_engine


# These are not fixtures, because depending on the setup, some of the object
# instantiations may fail
def mock_tesseract_engine():
    """Get the Dicom Redactor Engine."""
    return DicomImageRedactorEngine()


def mock_di_engine():
    """Build the Dicom Redactor Engine with Document Intelligence OCR."""
    di_ocr = DocumentIntelligenceOCR()
    ia_engine = ImageAnalyzerEngine(ocr=di_ocr)
    return DicomImageRedactorEngine(image_analyzer_engine=ia_engine)


def all_engines_required():
    """Return all required engines and their must_pass flag for tests."""
    return [(must_succeed(mock_tesseract_engine)),
            (allow_failure(mock_di_engine))]


@pytest.mark.parametrize(
    "dcm_filepath",
    [
        (Path(RESOURCES_PARENT_DIR, "0_ORIGINAL.dcm")),
        (Path(RESOURCES_DIR2, "1_ORIGINAL.dcm")),
        (Path(RESOURCES_DIR2, "2_ORIGINAL.dcm")),
    ],
)
@pytest.mark.parametrize("engine_builder", all_engines_required())
def test_redact_image_correctly(engine_builder: Callable, dcm_filepath: Path):
    """Test the redact function.

    Args:
        engine_builder: function returning a DicomImageRedactorEngine
        dcm_filepath (Path): Path to DICOM file to load.
    """
    test_image = pydicom.dcmread(dcm_filepath)
    test_redacted_image = engine_builder().redact(test_image, use_metadata=True)

    assert (
        np.array_equal(test_image.pixel_array, test_redacted_image.pixel_array) is False
    )


@pytest.mark.parametrize("engine_builder", all_engines_required())
def test_redact_from_single_file_correctly(engine_builder: Callable):
    """Test the redact_from_file function with single file case.

    Args:
        engine_builder: function returning a DicomImageRedactorEngine
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Set file paths and redact PII
        input_path = Path(RESOURCES_PARENT_DIR, "0_ORIGINAL.dcm")
        engine_builder().redact_from_file(
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
    """Test the redact_from_file function with multiple files case.

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
