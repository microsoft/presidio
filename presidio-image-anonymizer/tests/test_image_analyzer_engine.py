import pytest
from presidio_image_anonymizer.image_analyzer_engine import ImageAnalyzerEngine
from presidio_image_anonymizer.image_recognizer_result import ImageRecognizerResult
from presidio_analyzer import RecognizerResult


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

    analyzer_result = []
    analyzer_result.append(RecognizerResult("PERSON", 32, 37, 0.85))
    analyzer_result.append(RecognizerResult("PERSON", 39, 46, 0.85))

    return ocr_result, text, analyzer_result


@pytest.fixture(scope="function")
def get_image_recognizerresult():
    results = []
    results.append(ImageRecognizerResult("PERSON", 32, 37, 0.85, 896, 64, 183, 40))
    results.append(ImageRecognizerResult("PERSON", 39, 46, 0.85, 141, 134, 190, 50))
    return results


def test_given_empty_dict_then_get_text_from_ocr_dict_returns_empty_str():
    ocr_result = {}
    expected_text = ""
    text = ImageAnalyzerEngine.get_text_from_ocr_dict(ocr_result)

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
    text = ImageAnalyzerEngine.get_text_from_ocr_dict(ocr_result, sep)
    assert expected_text == text


def test_given_wrong_keys_in_dict_then_get_text_from_ocr_dict_returns_exception():
    ocr_result = {"words": ["John"], "level": [0]}
    expected_exception_message = "Key 'text' not found in dictionary"
    with pytest.raises(KeyError) as e:
        ImageAnalyzerEngine.get_text_from_ocr_dict(ocr_result)
    assert expected_exception_message == e.value.args[0]


def test_given_valid_ocr_results_and_entities_then_map_entities_returns_correct_output(
    get_ocr_analyzer_results, get_image_recognizerresult
):
    ocr_result, text, recogniser_result = get_ocr_analyzer_results
    expected_result = get_image_recognizerresult
    mapped_entities = ImageAnalyzerEngine.map_entities(
        recogniser_result, ocr_result, text
    )

    assert len(expected_result) == len(mapped_entities)
    assert expected_result == mapped_entities


def test_given_empty_ocr_dict_and_entities_lists_then_map_entities_returns_empty_list(
    get_ocr_analyzer_results,
):
    ocr_result, text, recogniser_result = get_ocr_analyzer_results
    assert ImageAnalyzerEngine.map_entities([], {}, "") == []
    assert ImageAnalyzerEngine.map_entities([], ocr_result, text) == []
    assert ImageAnalyzerEngine.map_entities(recogniser_result, {}, "") == []


def test_given_wrong_keys_in_ocr_result_dict_then_map_entities_returns_exception():
    ocr_result = {"words": ["John"], "level": [0]}
    expected_exception_message = "Key 'text' not found in dictionary"
    with pytest.raises(KeyError) as e:
        ImageAnalyzerEngine.map_entities([], ocr_result, "")
    assert expected_exception_message == e.value.args[0]


def test_given_repeated_entities_then_map_entities_returns_correct_number_of_bboxes(
    get_ocr_analyzer_results,
):
    ocr_result, text, recogniser_result = get_ocr_analyzer_results

    ocr_result["text"][1] = "Katie"
    recogniser_result.append(RecognizerResult("PERSON", 1, 6, 0.85))
    text = " Katie Interiors was created by Katie  Cromley."

    assert (
        len(ImageAnalyzerEngine.map_entities(recogniser_result, ocr_result, text)) == 3
    )


def test_given_word_has_entity_but_not_entity_then_map_entity_returns_correct_bboxes(
    get_ocr_analyzer_results, get_image_recognizerresult
):
    ocr_result, text, recogniser_result = get_ocr_analyzer_results
    ocr_result["text"][2] = "Katieiors"
    text = " Homey Katieiors was created by Katie  Cromley."
    expected_result = get_image_recognizerresult
    mapped_entities = ImageAnalyzerEngine.map_entities(
        recogniser_result, ocr_result, text
    )

    assert len(expected_result) == len(mapped_entities)
    assert expected_result == mapped_entities


def test_given_entity_with_multiple_words_then_map_entities_returns_correct_bboxees(
    get_ocr_analyzer_results,
):
    ocr_result, text, recogniser_result = get_ocr_analyzer_results

    # create new object for multiple words entities
    recogniser_result = [RecognizerResult("PERSON", 32, 46, 0.85)]
    expected_result = []
    expected_result.append(
        ImageRecognizerResult("PERSON", 32, 46, 0.85, 896, 64, 183, 40)
    )
    expected_result.append(
        ImageRecognizerResult("PERSON", 32, 46, 0.85, 141, 134, 190, 50)
    )
    mapped_entities = ImageAnalyzerEngine.map_entities(
        recogniser_result, ocr_result, text
    )

    assert len(expected_result) == len(mapped_entities)
    assert expected_result == mapped_entities
