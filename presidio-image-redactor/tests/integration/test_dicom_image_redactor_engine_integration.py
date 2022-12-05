"""Integration test for the DicomImageRedactorEngine class

Note that we are not asserting every pixel is equal when comparing original to redacted images
to account for differences in performance with different versions of Tesseract OCR.
"""
import tempfile
import pydicom
from pathlib import Path
from presidio_image_redactor.utils.dicom_image_utils import get_all_dcm_files
from presidio_image_redactor.dicom_image_redactor_engine import DicomImageRedactorEngine

RESOURCES_PARENT_DIR = "presidio-image-redactor/tests/integration/resources"
RESOURCES_DIR1 = "presidio-image-redactor/tests/integration/resources/dir1"


def test_redact_from_single_file_correctly():
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Set file paths and redact PII
        input_path = Path(RESOURCES_PARENT_DIR, "0_ORIGINAL.dcm")
        engine = DicomImageRedactorEngine()
        engine.redact(
            input_dicom_path=str(input_path),
            output_dir=tmpdirname,
            box_color_setting="contrast",
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


def test_redact_from_directory_correctly():
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Set file paths and redact PII
        input_path = Path(RESOURCES_DIR1)
        engine = DicomImageRedactorEngine()
        engine.redact(
            input_dicom_path=str(input_path),
            output_dir=tmpdirname,
            box_color_setting="contrast",
        )
        output_files = get_all_dcm_files(Path(tmpdirname))

        assert len(output_files) == len(get_all_dcm_files(input_path))
