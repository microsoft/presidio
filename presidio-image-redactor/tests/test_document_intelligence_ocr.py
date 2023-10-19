import pytest
from unittest import mock
from presidio_image_redactor.document_intelligence_ocr import DocumentIntelligenceOCR
from azure.ai.formrecognizer import AnalyzeResult


@pytest.fixture(scope="module")
def ocr_response(request):
    return AnalyzeResult.from_dict(request.param)


@pytest.mark.parametrize("ocr_response, expected",
[
    # Base Case 
    ({"pages": [{"words": []}]}, 
        {"left": [], "top": [], "width": [], "height": [], "conf": [], "text": []}),
    # Polygon of sequence 0 are invalid
    ({"pages": [{"words": [{"content": "Happy", "confidence": 3.14, "polygon": []}]}]},
        {"left": [0], "top": [0], "width": [0], "height": [0], "conf": [3.14], "text": ["Happy"]}),
    # Polygon of sequence 1 are invalid
    ({"pages": [{"words": [{"content": "Happy", "confidence": 3.14, "polygon": [{"x": 1, "y": 2}]}]}]}, 
        {"left": [0], "top": [0], "width": [0], "height": [0], "conf": [3.14], "text": ["Happy"]}),
    # Regular two point polygon
    ({"pages": [{"words": [{"content": "Happy", "confidence": 3.14, "polygon": [{"x": 1, "y": 2}, {"x": 3, "y": 42}]}]}]},
        {"left": [1], "top": [2], "width": [2], "height": [40], "conf": [3.14], "text": ["Happy"]}),
    # Order doesn't matter
    ({"pages": [{"words": [{"content": "Happy", "confidence": 3.14, "polygon": [{"x": 3, "y": 42}, {"x": 1, "y": 2}]}]}]},
        {"left": [1], "top": [2], "width": [2], "height": [40], "conf": [3.14], "text": ["Happy"]}),
    # Can specify other corners
    ({"pages": [{"words": [{"content": "Happy", "confidence": 3.14, "polygon": [{"x": 3, "y": 2}, {"x": 1, "y": 42}]}]}]},
        {"left": [1], "top": [2], "width": [2], "height": [40], "conf": [3.14], "text": ["Happy"]}),
],
indirect=["ocr_response"])
def test_given_da_response_then_get_bboxes_matches(ocr_response, expected):
    """Test that the bounding boxes are correctly extracted from the OCR response.
    
    :param ocr_response: The OCR response from the Document Intelligence client
    :param expected: The expected bounding boxes
    """
    result = DocumentIntelligenceOCR._page_to_bboxes(ocr_response.pages[0])
    assert expected == result

@pytest.mark.parametrize("ocr_response",
    [
        # word is incorrect
        ({"pages": [{"word": []}]})
    ])
def test_given_wrong_keys_in_response_then_parsing_fails_returns_exception(ocr_response):
    """Test parsing failures.
    
    :param ocr_response: The OCR response from the Document Intelligence client
    """
    with pytest.raises(AttributeError):
        DocumentIntelligenceOCR._page_to_bboxes(ocr_response.pages[0])

def test_model_id_wrong_then_raises_exception():
    """Test an incorrect model raises an exception"""
    with pytest.raises(ValueError):
        DocumentIntelligenceOCR(key="fake_key", endpoint="fake_endpoint", model_id = "fake_model_id")

def test_model_id_correct_then_raises_no_exception():
    """Confirm that there's no exception if the model_id is correct"""
    DocumentIntelligenceOCR(key="fake_key", endpoint="fake_endpoint", model_id = "prebuilt-document")

@pytest.mark.parametrize("result, ok",
    [
        ({"pages": []}, False),
        ({"pages": [{"words": []}]}, True),
        ({"pages": [{"words": []}, {"words": []}]}, False),
    ]
)
@mock.patch("presidio_image_redactor.document_intelligence_ocr.DocumentIntelligenceOCR.analyze_document")
def test_pages_not_one_then_raises_exception(analyze_document, result, ok: bool):
    """Test that the number of pages is exactly one.

    :param analyze_document: The mocked analyze_document function
    :param result: The result to return from the mocked analyze_document function
    :param ok: Whether the test should pass or fail
    """
    ocr_result = AnalyzeResult.from_dict(result)
    diOCR = DocumentIntelligenceOCR(endpoint="fake_endpoint", key="fake_key")
    diOCR.analyze_document.return_value = ocr_result
    if not ok:
        with pytest.raises(ValueError):
            diOCR.perform_ocr(b"")
    else:
        diOCR.perform_ocr(b"")


def test_ocr_endpoint_via_environment_vars_then_valid_response(get_mock_png):
    """Test that the OCR endpoint returns a valid response.
    
    :param get_mock_png: The mock PNG image
    """
    try:
        di_ocr = DocumentIntelligenceOCR()
    except Exception:
        pytest.skip("Environment variables not set")
    result = di_ocr.perform_ocr(get_mock_png)
    assert isinstance(result, dict)
    assert "text" in result
    assert "DAVIDSON" in result["text"]