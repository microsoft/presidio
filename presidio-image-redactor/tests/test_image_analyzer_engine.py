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
        recognizer_result, ocr_result, text
    )

    assert len(expected_result) == len(mapped_entities)
    assert expected_result == mapped_entities


def test_given_empty_ocr_entities_lists_then_map_analyzer_results_returns_empty_list(
    get_ocr_analyzer_results,
):
    ocr_result, text, recognizer_result = get_ocr_analyzer_results
    assert ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes([], {}, "") == []
    assert (
        ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes([], ocr_result, text)
        == []
    )
    assert (
        ImageAnalyzerEngine.map_analyzer_results_to_bounding_boxes(
            recognizer_result, {}, ""
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
            recognizer_result, ocr_result, ""
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
                recognizer_result, ocr_result, text
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
        recognizer_result, ocr_result, text
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
        recognizer_result, ocr_result, text
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
        recognizer_result, ocr_result, text
    )

    assert len(expected_result) == len(mapped_entities)
    assert expected_result == mapped_entities
