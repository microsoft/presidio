import pytest
from presidio_analyzer import RecognizerResult

from presidio_image_redactor import ImageAnalyzerEngine
from presidio_image_redactor.entities import ImageRecognizerResult


def test_given_valid_ocr_and_entities_then_map_analyzer_returns_correct_len_and_output(
    get_ocr_analyzer_results, get_image_recognizerresult
):
    ocr_result, text, recognizer_result = get_ocr_analyzer_results

    expected_result = get_image_recognizerresult
    mapped_entities = ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
        recognizer_result, ocr_result, text, []
    )

    assert len(expected_result) == len(mapped_entities)
    assert expected_result == mapped_entities

def test_given_allow_list_then_map_analyzer_results_contain_allowed_words(
    get_ocr_analyzer_results
):
    ocr_result, text, recognizer_result = get_ocr_analyzer_results
    mapped_entities = ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
        recognizer_result, ocr_result, text, allow_list=["Katie", "Cromley."]
    )

    assert len(mapped_entities) == 0

def test_given_empty_ocr_entities_lists_then_map_analyzer_results_returns_empty_list(
    get_ocr_analyzer_results,
):
    ocr_result, text, recognizer_result = get_ocr_analyzer_results
    assert ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes([], {}, "", []) == []
    assert (
        ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes([], ocr_result, text, [])
        == []
    )
    assert (
        ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
            recognizer_result, {}, "", []
        )
        == []
    )


def test_given_wrong_keys_in_ocr_dict_then_map_analyzer_results_returns_exception(
    get_ocr_analyzer_results,
):
    ocr_result, text, recognizer_result = get_ocr_analyzer_results
    ocr_result = {"words": ["John"], "level": [0]}
    with pytest.raises(KeyError):
        ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
            recognizer_result, ocr_result, "", []
        )


def test_given_repeat_entities_then_map_analyzer_results_returns_correct_no_of_bboxes(
    get_ocr_analyzer_results,
):
    ocr_result, text, recognizer_result = get_ocr_analyzer_results

    ocr_result["text"][1] = "Katie"
    recognizer_result.append(RecognizerResult("PERSON", 1, 6, 0.85))
    text = " Katie Interiors was created by Katie  Cromley."

    assert (
        len(
            ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
                recognizer_result, ocr_result, text, []
            )
        )
        == 3
    )


def test_given_word_has_entity_but_not_entity_then_map_entity_correct_bboxes_and_len(
    get_ocr_analyzer_results, get_image_recognizerresult
):
    ocr_result, text, recognizer_result = get_ocr_analyzer_results
    ocr_result["text"][2] = "Katieiors"
    text = " Homey Katieiors was created by Katie  Cromley."
    expected_result = get_image_recognizerresult
    mapped_entities = ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
        recognizer_result, ocr_result, text, []
    )

    assert len(expected_result) == len(mapped_entities)
    assert expected_result == mapped_entities


def test_given_multiword_entity_then_map_analyzer_returns_correct_bboxes_and_len(
    get_ocr_analyzer_results,
):
    ocr_result, text, recognizer_result = get_ocr_analyzer_results

    # create new object for multiple words entities
    recognizer_result = [RecognizerResult("PERSON", 32, 46, 0.85)]
    expected_result = [
        ImageRecognizerResult("PERSON", 32, 46, 0.85, 896, 64, 183, 40),
        ImageRecognizerResult("PERSON", 32, 46, 0.85, 141, 134, 190, 50),
    ]
    mapped_entities = ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
        recognizer_result, ocr_result, text, []
    )

    assert len(expected_result) == len(mapped_entities)
    assert expected_result == mapped_entities


def test_given_dif_len_entities_then_map_analyzer_returns_correct_outputand_len(
    get_ocr_analyzer_results, get_image_recognizerresult
):
    ocr_result, text, recognizer_result = get_ocr_analyzer_results
    recognizer_result[1].start += 1
    expected_result = get_image_recognizerresult
    expected_result[1].start += 1
    mapped_entities = ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
        recognizer_result, ocr_result, text, []
    )

    assert len(expected_result) == len(mapped_entities)
    assert expected_result == mapped_entities


@pytest.mark.parametrize(
    "ocr_threshold, expected_length",
    [(-1, 9), (50, 7), (80, 2), (100, 0)],
)
def test_threshold_ocr_result_returns_expected_results(
    image_analyzer_engine, ocr_threshold, expected_length
):
    # Assign
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
    ocr_result["conf"] = [-1, 99.5, 92.3, 42.7, 66.1, 51.2, 79.7, 64.0, 70.3]

    # Act
    test_filtered = image_analyzer_engine.threshold_ocr_result(
        ocr_result, ocr_threshold
    )

    # Assert
    assert len(test_filtered["conf"]) == expected_length


def test_remove_space_boxes_happy_path(
    image_analyzer_engine
):
    # Arrange
    ocr_result = {
        "text": ["John", " ", "Doe", "", "  "],
        "left": [100, 0, 275, 415, 999],
        "top": [5, 315, 900, 0, 17]
    }

    # Act
    test_results = image_analyzer_engine.remove_space_boxes(ocr_result)

    # Assert
    assert len(test_results["text"]) == 2
    assert test_results["text"] == ["John","Doe"]
    assert test_results["left"] == [100, 275]
    assert test_results["top"] == [5, 900]


@pytest.mark.parametrize(
    "text_analyzer_kwargs, expected_allow_list",
    [
        (None, []),
        (
            {
                "arg1": 1,
                "arg2": 2,
                "allow_list": ["a", "b", "c"]
            },
            ["a", "b", "c"]
        ),
        (
            {
                "arg1": 1,
                "arg2": 2,
                "allow_list": []
            },
            []
        )
    ],
)
def test_check_for_allow_list_happy_path(
    image_analyzer_engine: ImageAnalyzerEngine,
    text_analyzer_kwargs: dict,
    expected_allow_list: list
):
    # Act
    test_allow_list = image_analyzer_engine._check_for_allow_list(text_analyzer_kwargs)

    # Assert
    assert test_allow_list == expected_allow_list
