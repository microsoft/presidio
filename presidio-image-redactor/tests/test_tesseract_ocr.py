import pytest
from presidio_image_redactor.tesseract_ocr import TesseractOCR


def test_given_empty_dict_then_get_text_from_ocr_dict_returns_empty_str():
    ocr_result = {}
    expected_text = ""
    text = TesseractOCR.get_text_from_ocr_dict(ocr_result)

    assert expected_text == text


@pytest.mark.parametrize(
    "sep, expected_text",
    [
        (" ", " Homey Interiors was created by Katie  Cromley."),
        ("+", "+Homey+Interiors+was+created+by+Katie++Cromley."),
    ],
)
def test_given_valid_dict_then_get_text_from_ocr_dict_returns_correct_str(
    get_ocr_analyzer_results, sep, expected_text
):
    ocr_result, t, a = get_ocr_analyzer_results
    text = TesseractOCR.get_text_from_ocr_dict(ocr_result, sep)
    assert expected_text == text


def test_given_wrong_keys_in_dict_then_get_text_from_ocr_dict_returns_exception():
    ocr_result = {"words": ["John"], "level": [0]}
    with pytest.raises(KeyError):
        TesseractOCR.get_text_from_ocr_dict(ocr_result)
