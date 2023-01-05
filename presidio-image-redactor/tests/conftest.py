import pydicom
import json
import os
from presidio_analyzer.recognizer_result import RecognizerResult

from presidio_image_redactor import ImageAnalyzerEngine
from presidio_image_redactor.entities import ImageRecognizerResult
import pytest

SCRIPT_DIR = os.path.dirname(__file__)


@pytest.fixture(scope="function")
def get_ocr_analyzer_results():
    ocr_result = {}
    ocr_result["text"] = [
        "",
        "Homey",
        "Interiors",
        "was",
        "created",
        "by",
        "Katie",
        "",
        "Cromley.",
    ]
    ocr_result["left"] = [143, 143, 322, 530, 634, 827, 896, 141, 141]
    ocr_result["top"] = [64, 67, 67, 76, 64, 64, 64, 134, 134]
    ocr_result["width"] = [936, 160, 191, 87, 172, 51, 183, 801, 190]
    ocr_result["height"] = [50, 47, 37, 28, 40, 50, 40, 50, 50]
    text = " Homey Interiors was created by Katie  Cromley."

    analyzer_result = [
        RecognizerResult("PERSON", 32, 37, 0.85),
        RecognizerResult("PERSON", 39, 46, 0.85),
    ]

    return ocr_result, text, analyzer_result


@pytest.fixture(scope="function")
def get_image_recognizerresult():
    results = [
        ImageRecognizerResult("PERSON", 32, 37, 0.85, 896, 64, 183, 40),
        ImageRecognizerResult("PERSON", 39, 46, 0.85, 141, 134, 190, 50),
    ]
    return results


@pytest.fixture(scope="module")
def image_analyzer_engine():
    return ImageAnalyzerEngine()


@pytest.fixture(scope="module")
def get_mock_dicom_instance():
    """DICOM instance to use in testing"""
    # Assign
    filepath = f"{SCRIPT_DIR}/test_data/0_ORIGINAL.dcm"

    # Act
    instance = pydicom.dcmread(filepath)

    return instance


@pytest.fixture(scope="module")
def get_mock_dicom_verify_results():
    """Loaded json results file"""
    with open(
        f"{SCRIPT_DIR}/integration/resources/dicom_pii_verify_integration.json"
    ) as json_file:
        results_json = json.load(json_file)

    return results_json
