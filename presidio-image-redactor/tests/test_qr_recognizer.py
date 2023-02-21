import cv2
import numpy as np

import pytest

from tests.integration.methods import get_resource_image

from presidio_image_redactor.qr_recognizer import (
    OpenCVQRRecongnizer,
    QRRecognizerResult,
)


@pytest.fixture(scope="module")
def opencv_qr_recognizer():
    return OpenCVQRRecongnizer()


def test_given_image_with_qr_then_opencvqrrecognizer_returns_expected_results(
    opencv_qr_recognizer,
):
    image = get_resource_image("qr.png")
    recognized = opencv_qr_recognizer.recognize(image)

    assert len(recognized) == 1
    assert recognized[0] == QRRecognizerResult(
        text="https://github.com/microsoft/presidio",
        bbox=[71, 71, 1013, 1013],
        polygon=[71, 71, 1083, 71, 1083, 1083, 71, 1083, 71, 71],
    )


def test_given_image_without_qr_then_opencvqrrecognizer_returns_empty_list(
    opencv_qr_recognizer,
):
    image = get_resource_image("no_ocr.jpg")
    recognized = opencv_qr_recognizer.recognize(image)

    assert len(recognized) == 0
