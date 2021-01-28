import pytest
from presidio_image_anonymizer.image_analyzer_engine import ImageAnalyzerEngine
from presidio_image_anonymizer.image_recognizer_result import ImageRecognizerResult
from presidio_analyzer import RecognizerResult


@pytest.fixture(scope="module")
def get_ocr_results():
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

    return ocr_result


@pytest.fixture(scope="module")
def get_recognizerresult():
    results = []
    results.append(RecognizerResult("PERSON", 31, 38, 0.85))
    results.append(RecognizerResult("PERSON", 39, 46, 0.85))
    return results


@pytest.fixture(scope="module")
def get_image_recognizerresult():
    results = []
    results.append(ImageRecognizerResult("PERSON", 31, 38, 0.85, 896, 64, 183, 40))
    results.append(ImageRecognizerResult("PERSON", 39, 46, 0.85, 141, 134, 50))
    return results


def test_given_empty_dict_then_get_text_from_ocr_dict_returns_empty_str():
    ocr_result = {}
    expected_text = ""
    text = ImageAnalyzerEngine.get_text_from_ocr_dict(ocr_result)

    assert expected_text == text


def test_given_valid_dict_then_get_text_from_ocr_dict_returns_correct_str(
    get_ocr_results,
):
    ocr_result = get_ocr_results
    expected_text = "Homey Interiors was created by Katie Cromley."
    text = ImageAnalyzerEngine.get_text_from_ocr_dict(ocr_result)

    assert expected_text == text


def test_given_wrong_keys_in_dict_then_get_text_from_ocr_dict_returns_exception():
    ocr_result = {"words": ["John"], "level": [0]}
    expected_exception_message = "Key 'text' not found in dictionary"
    with pytest.raises(KeyError) as e:
        ImageAnalyzerEngine.get_text_from_ocr_dict(ocr_result)
    assert expected_exception_message == e.value.err_msg


def test_given_valid_ocr_results_and_entities_then_map_entities_returns_correct_output(
    get_ocr_results, get_recognizerresult, get_image_recognizerresult
):
    ocr_result = get_ocr_results
    recogniser_result = get_recognizerresult
    expected_result = get_image_recognizerresult
    mapped_entities = ImageAnalyzerEngine.map_entities(recogniser_result, ocr_result)

    assert expected_result == mapped_entities


def test_given_empty_ocr_dict_and_entities_lists_then_map_entities_returns_empty_list(
    get_ocr_results, get_recognizerresult
):
    ocr_result = get_ocr_results
    recogniser_result = get_recognizerresult
    assert ImageAnalyzerEngine.map_entities([], {}) == []
    assert ImageAnalyzerEngine.map_entities([], ocr_result) == []
    assert ImageAnalyzerEngine.map_entities(recogniser_result, {}) == []


def test_given_wrong_keys_in_ocr_result_dict_then_map_entities_returns_exception():
    ocr_result = {"words": ["John"], "level": [0]}
    expected_exception_message = "Key 'text' not found in dictionary"
    with pytest.raises(KeyError) as e:
        ImageAnalyzerEngine.map_entities([], ocr_result)
    assert expected_exception_message == e.value.err_msg


def test_given_repeated_entities_then_map_entities_returns_correct_number_of_bboxes(
    get_ocr_results, get_recognizerresult
):
    ocr_result = get_ocr_results
    recogniser_result = get_recognizerresult

    ocr_result["text"][1] = "Katie"
    recogniser_result.append(RecognizerResult("PERSON", 0, 15, 0.85, 143, 67, 160, 47))

    assert len(ImageAnalyzerEngine.map_entities(recogniser_result, ocr_result)) == 3


def test_given_word_has_entity_but_not_entity_then_map_entity_returns_correct_bboxes(
    get_ocr_results, get_recognizerresult, get_image_recognizerresult
):
    ocr_result = get_ocr_results
    ocr_result["text"][2] = "Katieiors"
    recogniser_result = get_recognizerresult
    expected_result = get_image_recognizerresult
    mapped_entities = ImageAnalyzerEngine.map_entities(recogniser_result, ocr_result)

    assert expected_result == mapped_entities
