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
    with pytest.raises(KeyError):
        ImageAnalyzerEngine.get_text_from_ocr_dict(ocr_result)


def test_given_valid_ocr_and_entities_then_map_analyzer_results_returns_correct_output(
    get_ocr_analyzer_results, get_image_recognizerresult
):
    ocr_result, text, recogniser_result = get_ocr_analyzer_results
    expected_result = get_image_recognizerresult
    mapped_entities = ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
        recogniser_result, ocr_result, text
    )

    assert len(expected_result) == len(mapped_entities)
    assert expected_result == mapped_entities


def test_given_empty_ocr_entities_lists_then_map_analyzer_results_returns_empty_list(
    get_ocr_analyzer_results,
):
    ocr_result, text, recogniser_result = get_ocr_analyzer_results
    assert ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes([], {}, "") == []
    assert (
        ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes([], ocr_result, text)
        == []
    )
    assert (
        ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
            recogniser_result, {}, ""
        )
        == []
    )


def test_given_wrong_keys_in_ocr_dict_then_map_analyzer_results_returns_exception(
    get_ocr_analyzer_results,
):
    ocr_result, text, recogniser_result = get_ocr_analyzer_results
    ocr_result = {"words": ["John"], "level": [0]}
    with pytest.raises(KeyError):
        ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
            recogniser_result, ocr_result, ""
        )


def test_given_repeat_entities_then_map_analyzer_results_returns_correct_no_of_bboxes(
    get_ocr_analyzer_results,
):
    ocr_result, text, recogniser_result = get_ocr_analyzer_results

    ocr_result["text"][1] = "Katie"
    recogniser_result.append(RecognizerResult("PERSON", 1, 6, 0.85))
    text = " Katie Interiors was created by Katie  Cromley."

    assert (
        len(
            ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
                recogniser_result, ocr_result, text
            )
        )
        == 3
    )


def test_given_word_has_entity_but_not_entity_then_map_entity_returns_correct_bboxes(
    get_ocr_analyzer_results, get_image_recognizerresult
):
    ocr_result, text, recogniser_result = get_ocr_analyzer_results
    ocr_result["text"][2] = "Katieiors"
    text = " Homey Katieiors was created by Katie  Cromley."
    expected_result = get_image_recognizerresult
    mapped_entities = ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
        recogniser_result, ocr_result, text
    )

    assert len(expected_result) == len(mapped_entities)
    assert expected_result == mapped_entities


def test_given_multiword_entity_then_map_analyzer_results__returns_correct_bboxes(
    get_ocr_analyzer_results,
):
    ocr_result, text, recogniser_result = get_ocr_analyzer_results

    # create new object for multiple words entities
    recogniser_result = [RecognizerResult("PERSON", 32, 46, 0.85)]
    expected_result = [
        ImageRecognizerResult("PERSON", 32, 46, 0.85, 896, 64, 183, 40),
        ImageRecognizerResult("PERSON", 32, 46, 0.85, 141, 134, 190, 50),
    ]
    mapped_entities = ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
        recogniser_result, ocr_result, text
    )

    assert len(expected_result) == len(mapped_entities)
    assert expected_result == mapped_entities


def test_given_dif_len_entities_then_map_analyzer_results_returns_correct_output(
    get_ocr_analyzer_results, get_image_recognizerresult
):
    ocr_result, text, recogniser_result = get_ocr_analyzer_results
    recogniser_result[1].start += 1
    expected_result = get_image_recognizerresult
    expected_result[1].start += 1
    mapped_entities = ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
        recogniser_result, ocr_result, text
    )

    assert len(expected_result) == len(mapped_entities)
    assert expected_result == mapped_entities
