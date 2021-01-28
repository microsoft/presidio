import pytest
from presidio_image_anonymizer.image_analyzer_engine import ImageAnalyzerEngine


def test_given_empty_dict_then_get_text_from_ocr_dict_returns_empty_str():
    ocr_result = {}
    expected_text = ""
    text = ImageAnalyzerEngine.get_text_from_ocr_dict(ocr_result)

    assert expected_text == text


def test_given_valid_dict_then_get_text_from_ocr_dict_returns_correct_str():
    ocr_result = {
        "text": [
            "",
            "",
            "",
            "",
            "This",
            "project",
            "is",
            "created",
            "by",
            "David",
            "Johnson.",
        ]
    }
    expected_text = "This project is created by David Johnson."
    text = ImageAnalyzerEngine.get_text_from_ocr_dict(ocr_result)

    assert expected_text == text


def test_given_wrong_keys_in_dict_then_get_text_from_ocr_dict_returns_exception():
    ocr_result = {"words": ["John"], "level": [0]}
    expected_exception_message = "Key 'text' not found in dictionary"
    with pytest.raises(KeyError) as e:
        ImageAnalyzerEngine.get_text_from_ocr_dict(ocr_result)
    assert expected_exception_message == e.value.err_msg
