import pytest
from methods import get_resource_image
from presidio_image_redactor import ImageAnalyzerEngine
from presidio_image_redactor.entities import ImageRecognizerResult


@pytest.mark.skip(reason="different results with tesseract 4.0 vs 5.0")
def test_given_image_then_text_entities_are_recognized_correctly():
    # TODO fix in bug #2897

    # Image with PII entities
    image = get_resource_image("ocr_test.png")
    analyzer_results = ImageAnalyzerEngine().analyze(image)
    assert len(analyzer_results) == 7
    results = __get_expected_ocr_test_image_analysis_results()
    for i in range(7):
        assert analyzer_results[i] == results[i]


def test_given_image_without_text_then_no_entities_recognized():
    # Image without PII entities
    image = get_resource_image("no_ocr.jpg")
    analyzer_results = ImageAnalyzerEngine().analyze(image)
    assert len(analyzer_results) == 0


def __get_expected_ocr_test_image_analysis_results():
    return [
        ImageRecognizerResult("PERSON", 31, 44, 0.85, 472, 20, 91, 31),
        ImageRecognizerResult("PERSON", 31, 44, 0.85, 576, 20, 147, 31),
        ImageRecognizerResult("DOMAIN_NAME", 303, 320, 1.0, 28, 299, 438, 38),
        ImageRecognizerResult("PHONE_NUMBER", 332, 346, 0.7, 666, 298, 88, 40),
        ImageRecognizerResult("PHONE_NUMBER", 332, 346, 0.7, 769, 301, 169, 29),
        ImageRecognizerResult("EMAIL_ADDRESS", 772, 794, 1.0, 27, 912, 458, 39),
        ImageRecognizerResult("DOMAIN_NAME", 781, 794, 1.0, 27, 912, 458, 39),
    ]
