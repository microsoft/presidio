"""Test suite for dicom_image_redact_utils.py"""
from pathlib import Path
import numpy as np
import pydicom
import presidio_image_redactor
from presidio_image_redactor.entities.image_recognizer_result import (
    ImageRecognizerResult,
)
import presidio_analyzer
import pytest
from typing import Union, Tuple
from presidio_image_redactor.utils.dicom_image_redact_utils import (
    get_text_metadata,
    process_names,
    add_known_generic_phi,
    make_phi_list,
    create_custom_recognizer,
    get_bboxes_from_analyzer_results,
    format_bboxes,
    set_bbox_color,
    add_redact_box,
)

TEST_DICOM_PARENT_DIR = "presidio-image-redactor/tests/test_data"
TEST_DICOM_DIR_1 = "presidio-image-redactor/tests/test_data/dicom_dir_1"
TEST_DICOM_DIR_2 = "presidio-image-redactor/tests/test_data/dicom_dir_1/dicom_dir_2"
TEST_DICOM_DIR_3 = "presidio-image-redactor/tests/test_data/dicom_dir_1/dicom_dir_3"
TEST_NUMPY_DIR = "presidio-image-redactor/tests/test_data/numpy_arrays"
TEST_PNG_DIR = "presidio-image-redactor/tests/test_data/png_images"

# ------------------------------------------------------
# get_text_metadata()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "dcm_path, metadata_text_len, is_name_true_len, is_patient_true_len",
    [
        (Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"), 82, 4, 6),
        (Path(TEST_DICOM_PARENT_DIR, "RGB_ORIGINAL.dcm"), 93, 9, 10),
        (Path(TEST_DICOM_DIR_2, "1_ORIGINAL.DCM"), 83, 9, 8),
        (Path(TEST_DICOM_DIR_2, "2_ORIGINAL.dicom"), 118, 6, 10),
        (Path(TEST_DICOM_DIR_3, "3_ORIGINAL.DICOM"), 135, 8, 10),
    ],
)
def test_get_text_metadata_happy_path(
    dcm_path: Path,
    metadata_text_len: int,
    is_name_true_len: int,
    is_patient_true_len: int,
):
    """Test happy path for get_text_metadata

    Args:
        dcm_path (pathlib.Path): Path to DICOM file.
        metadata_text_len (int): Length of the expected returned metadata_text list.
        is_name_true_len (int): Number of true values in the returned is_name list.
        is_patient_true_len (int): Number of true values in the returned is_name list.
    """
    # Arrange
    test_instance = pydicom.dcmread(dcm_path)

    # Act
    test_metadata_text, test_is_name, test_is_patient = get_text_metadata(test_instance)

    # Assert
    idx_is_name = list(np.where(np.array(test_is_name) == True)[0])
    idx_is_patient = list(np.where(np.array(test_is_patient) == True)[0])

    assert len(test_metadata_text) == len(test_is_name) == len(test_is_patient)
    assert len(idx_is_name) == is_name_true_len
    assert len(idx_is_patient) == is_patient_true_len
    assert type(test_metadata_text[idx_is_name[0]]) == str


# ------------------------------------------------------
# process_names()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "text_metadata, is_name, expected_phi_list",
    [
        ([], [], []),
        (
            ["JOHN^DOE", "City Hospital", "12345"],
            [True, False, False],
            [
                "JOHN^DOE",
                "City Hospital",
                "12345",
                "JOHN",
                "DOE",
                "John",
                "Doe",
                "john",
                "doe",
                "JOHN DOE",
                "John Doe",
                "john doe",
            ],
        ),
    ],
)
def test_process_names_happy_path(
    text_metadata: list, is_name: list, expected_phi_list: list
):
    """Test happy path for process_names

    Args:
        text_metadata (list): List of text metadata.
        is_name (list): Whether each element is a name or not.
        expected_phi_list (list): List of expected output.
    """
    # Arrange

    # Act
    test_phi_list = process_names(text_metadata, is_name)

    # Assert
    assert set(test_phi_list) == set(expected_phi_list)


# ------------------------------------------------------
# add_known_generic_phi()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "phi_list, expected_return_list",
    [
        ([], ["M", "[M]", "F", "[F]", "X", "[X]", "U", "[U]"]),
        (
            ["JOHN^DOE", "City Hospital", "12345"],
            [
                "JOHN^DOE",
                "City Hospital",
                "12345",
                "M",
                "[M]",
                "F",
                "[F]",
                "X",
                "[X]",
                "U",
                "[U]",
            ],
        ),
    ],
)
def test_add_known_generic_phi_happy_path(phi_list: list, expected_return_list: list):
    """Test happy path for add_known_generic_phi

    Args:
        phi_list (list): List of PHI.
        expected_return_list (list): List of expected output.
    """
    # Arrange

    # Act
    test_phi_list = add_known_generic_phi(phi_list)

    # Assert
    assert set(test_phi_list) == set(expected_return_list)


# ------------------------------------------------------
# make_phi_list()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "original_metadata, mock_process_names_val, mock_add_known_val, expected_return_list",
    [
        (
            [
                ["A", "B"],
                "A",
                123,
                "JOHN^DOE",
                "City Hospital",
                "12345",
            ],
            [
                ["A", "B"],
                "A",
                123,
                "JOHN^DOE",
                "City Hospital",
                "12345",
                "JOHN",
                "DOE",
                "John",
                "Doe",
                "john",
                "doe",
                "JOHN DOE",
                "John Doe",
                "john doe",
            ],
            [
                ["A", "B"],
                "A",
                123,
                "JOHN^DOE",
                "City Hospital",
                "12345",
                "JOHN",
                "DOE",
                "John",
                "Doe",
                "john",
                "doe",
                "JOHN DOE",
                "John Doe",
                "john doe",
                "M",
                "[M]",
                "F",
                "[F]",
                "X",
                "[X]",
                "U",
                "[U]",
            ],
            [
                "A",
                "B",
                "123",
                "JOHN^DOE",
                "City Hospital",
                "12345",
                "JOHN",
                "DOE",
                "John",
                "Doe",
                "john",
                "doe",
                "JOHN DOE",
                "John Doe",
                "john doe",
                "M",
                "[M]",
                "F",
                "[F]",
                "X",
                "[X]",
                "U",
                "[U]",
            ],
        ),
    ],
)
def test_make_phi_list_happy_path(
    mocker,
    original_metadata: list,
    mock_process_names_val: list,
    mock_add_known_val: list,
    expected_return_list: list,
):
    """Test happy path for make_phi_list

    Args:
        original_metadata (list): List extracted metadata (excluding pixel array).
        mock_process_names_val (list): Value to provide to mock process_names.
        mock_add_known_val (list): Value to provide to mock add_known_generic_phi.
        expected_return_list (list): List of expected output.
    """
    # Arrange
    mock_process_names = mocker.patch(
        "presidio_image_redactor.utils.dicom_image_redact_utils.process_names",
        return_value=mock_process_names_val,
    )
    mock_add_known_generic_phi = mocker.patch(
        "presidio_image_redactor.utils.dicom_image_redact_utils.add_known_generic_phi",
        return_value=mock_add_known_val,
    )

    # Act
    test_phi_str_list = make_phi_list(original_metadata, [], [])

    # Assert
    assert mock_process_names.call_count == 1
    assert mock_add_known_generic_phi.call_count == 1
    assert set(test_phi_str_list) == set(expected_return_list)


# ------------------------------------------------------
# create_custom_recognizer()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "phi_list",
    [
        (
            [
                "JOHN^DOE",
                "City Hospital",
                "JOHN",
                "DOE",
                "John",
                "Doe",
                "john",
                "doe",
                "JOHN DOE",
                "John Doe",
                "john doe",
                "M",
                "[M]",
                "F",
                "[F]",
                "X",
                "[X]",
                "U",
                "[U]",
            ]
        ),
    ],
)
def test_create_custom_recognizer_happy_path(phi_list: list):
    """Test happy path for create_custom_recognizer

    Args:
        phi_list (list): List of phi.
        expected_return_list (list): List of expected output.
    """
    # Arrange

    # Act
    test_custom_analyzer_engine = create_custom_recognizer(phi_list)

    # Assert
    assert (
        type(test_custom_analyzer_engine)
        == presidio_image_redactor.image_analyzer_engine.ImageAnalyzerEngine
    )
    assert (
        type(test_custom_analyzer_engine.analyzer_engine.registry.recognizers[-1])
        == presidio_analyzer.pattern_recognizer.PatternRecognizer
    )


# ------------------------------------------------------
# get_bboxes_from_analyzer_results()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "analyzer_results, expected_bboxes_dict",
    [
        (
            [
                ImageRecognizerResult(
                    entity_type="TYPE_1",
                    start=0,
                    end=0,
                    left=25,
                    top=25,
                    width=100,
                    height=100,
                    score=0.99,
                ),
                ImageRecognizerResult(
                    entity_type="TYPE_2",
                    start=10,
                    end=10,
                    left=25,
                    top=49,
                    width=75,
                    height=51,
                    score=0.7,
                ),
                ImageRecognizerResult(
                    entity_type="TYPE_3",
                    start=25,
                    end=35,
                    left=613,
                    top=26,
                    width=226,
                    height=35,
                    score=0.6,
                ),
            ],
            {
                "0": {
                    "entity_type": "TYPE_1",
                    "score": 0.99,
                    "left": 25,
                    "top": 25,
                    "width": 100,
                    "height": 100,
                },
                "1": {
                    "entity_type": "TYPE_2",
                    "score": 0.7,
                    "left": 25,
                    "top": 49,
                    "width": 75,
                    "height": 51,
                },
                "2": {
                    "entity_type": "TYPE_3",
                    "score": 0.6,
                    "left": 613,
                    "top": 26,
                    "width": 226,
                    "height": 35,
                },
            },
        ),
    ],
)
def test_get_bboxes_from_analyzer_results_happy_path(
    analyzer_results: list, expected_bboxes_dict: dict
):
    """Test happy path for get_bboxes_from_analyzer_results

    Args:
        analyzer_results (list): Results from using ImageAnalyzerEngine.
        expected_bboxes_dict (dict): Expected output bounding box dictionary.
    """
    # Arrange

    # Act
    test_bboxes_dict = get_bboxes_from_analyzer_results(analyzer_results)

    # Assert
    assert test_bboxes_dict == expected_bboxes_dict


# ------------------------------------------------------
# format_bboxes()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "mock_intermediate_bbox, padding_width, expected_bboxes_dict",
    [
        (
            {
                "0": {
                    "entity_type": "TYPE_1",
                    "score": 0.99,
                    "left": 10,
                    "top": 15,
                    "width": 100,
                    "height": 100,
                },
                "1": {
                    "entity_type": "TYPE_2",
                    "score": 0.7,
                    "left": 25,
                    "top": 49,
                    "width": 75,
                    "height": 51,
                },
                "2": {
                    "entity_type": "TYPE_3",
                    "score": 0.6,
                    "left": 613,
                    "top": 26,
                    "width": 226,
                    "height": 35,
                },
            },
            25,
            [
                {"top": 0, "left": 0, "width": 100, "height": 100},
                {"top": 24, "left": 0, "width": 75, "height": 51},
                {"top": 1, "left": 588, "width": 226, "height": 35},
            ],
        ),
    ],
)
def test_format_bboxes_happy_path(
    mocker, mock_intermediate_bbox: dict, padding_width: int, expected_bboxes_dict: dict
):
    """Test happy path for format_bboxes

    Args:
        mock_intermediate_bbox (dict): Value for mock of get_bboxes_from_analyzer_results.
        padding_width (int): Pixel width used for padding.
        expected_bboxes_dict (dict): Expected output bounding box dictionary.
    """
    # Arrange
    mock_get_bboxes = mocker.patch(
        "presidio_image_redactor.utils.dicom_image_redact_utils.get_bboxes_from_analyzer_results",
        return_value=mock_intermediate_bbox,
    )

    # Act
    test_bboxes_dict = format_bboxes([], padding_width)

    # Assert
    assert mock_get_bboxes.call_count == 1
    assert test_bboxes_dict == expected_bboxes_dict


@pytest.mark.parametrize(
    "padding_width, expected_error_type",
    [(-1, "ValueError"), (-200, "ValueError")],
)
def test_format_bboxes_exceptions(padding_width: int, expected_error_type: str):
    """Test error handling of format_bboxes

    Args:
        padding_width (int): Pixel width used for padding.
        expected_error_type (str): Type of error we expect to be raised.
    """
    with pytest.raises(Exception) as exc_info:
        # Act
        _ = format_bboxes([], padding_width)

    # Assert
    assert expected_error_type == exc_info.typename


# ------------------------------------------------------
# set_bbox_color()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "box_color_setting, mock_box_color",
    [
        ("contrast", 0),
        ("contrast", (0, 0, 0)),
        ("background", 255),
        ("background", (255, 255, 255)),
    ],
)
def test_set_bbox_color_happy_path(
    mocker, box_color_setting: str, mock_box_color: Union[int, Tuple[int, int, int]]
):
    """Test happy path for set_bbox_color

    Args:
        box_color_setting (str): Determines how box color is selected.
        mock_box_color (int or Tuple of int): Color value to assign to mocker.
    """
    # Arrange
    test_instance = pydicom.dcmread(Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"))
    mock_convert_dcm_to_png = mocker.patch(
        "presidio_image_redactor.utils.dicom_image_redact_utils.convert_dcm_to_png",
        return_value=[None, True],
    )
    mock_Image_open = mocker.patch(
        "presidio_image_redactor.utils.dicom_image_redact_utils.Image.open",
        return_value=None,
    )
    mock_get_bg_color = mocker.patch(
        "presidio_image_redactor.utils.dicom_image_redact_utils.get_bg_color",
        return_value=mock_box_color,
    )

    # Act
    test_box_color = set_bbox_color(test_instance, box_color_setting)

    # Assert
    assert mock_convert_dcm_to_png.call_count == 1
    assert mock_Image_open.call_count == 1
    assert mock_get_bg_color.call_count == 1
    assert test_box_color == mock_box_color


@pytest.mark.parametrize(
    "box_color_setting, expected_error_type",
    [
        ("typo", "ValueError"),
        ("somecolor", "ValueError"),
        ("0", "ValueError"),
        ("255", "ValueError"),
    ],
)
def test_set_bbox_color_exceptions(box_color_setting: str, expected_error_type: str):
    """Test error handling of set_bbox_color

    Args:
        box_color_setting (str): Determines how box color is selected.
        expected_error_type (str): Type of error we expect to be raised.
    """
    with pytest.raises(Exception) as exc_info:
        # Arrange
        test_instance = pydicom.dcmread(Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"))

        # Act
        _ = set_bbox_color(test_instance, box_color_setting)

    # Assert
    assert expected_error_type == exc_info.typename


# ------------------------------------------------------
# add_redact_box()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "dcm_path, mock_is_greyscale, mock_box_color, bounding_boxes_coordinates",
    [
        (
            Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"),
            True,
            0,
            [
                {"top": 0, "left": 0, "width": 100, "height": 100},
                {"top": 24, "left": 0, "width": 75, "height": 51},
                {"top": 1, "left": 588, "width": 226, "height": 35},
            ],
        ),
        (
            Path(TEST_DICOM_PARENT_DIR, "RGB_ORIGINAL.dcm"),
            False,
            (0, 0, 0),
            [
                {"top": 0, "left": 0, "width": 500, "height": 500},
                {"top": 24, "left": 0, "width": 75, "height": 51},
                {"top": 1, "left": 588, "width": 100, "height": 100},
            ],
        ),
    ],
)
def test_add_redact_box_happy_path(
    mocker,
    dcm_path: Path,
    mock_is_greyscale: bool,
    mock_box_color: Union[int, Tuple[int, int, int]],
    bounding_boxes_coordinates: dict,
):
    """Test happy path for add_redact_box

    Args:
        dcm_path (pathlib.Path): Path to DICOM file.
        mock_is_greyscale (bool): Value to use when mocking check_if_greyscale.
        mock_box_color (int or Tuple of int): Color value to assign to mocker.
        bouding_boxes_coordinates (dict): Formatted bbox coordinates.
    """
    # Arrange
    test_instance = pydicom.dcmread(dcm_path)
    mock_check_if_greyscale = mocker.patch(
        "presidio_image_redactor.utils.dicom_image_redact_utils.check_if_greyscale",
        return_value=mock_is_greyscale,
    )
    mock_get_common_pixel = mocker.patch(
        "presidio_image_redactor.utils.dicom_image_redact_utils.get_most_common_pixel_value",
        return_value=mock_box_color,
    )
    mock_set_bbox_color = mocker.patch(
        "presidio_image_redactor.utils.dicom_image_redact_utils.set_bbox_color",
        return_value=mock_box_color,
    )

    # Act
    test_redacted_instance = add_redact_box(test_instance, bounding_boxes_coordinates)

    # Assert
    mock_check_if_greyscale.call_count == 1
    if mock_is_greyscale is True:
        original_pixel_values = np.array(test_instance.pixel_array).flatten()
        redacted_pixel_values = np.array(test_redacted_instance.pixel_array).flatten()
        box_color_pixels_original = len(
            np.where(original_pixel_values == mock_box_color)[0]
        )
        box_color_pixels_redacted = len(
            np.where(redacted_pixel_values == mock_box_color)[0]
        )
        mock_get_common_pixel.call_count == 1
    else:
        list_of_RGB_pixels_original = np.vstack(test_instance.pixel_array).tolist()
        list_of_RGB_pixels_redacted = np.vstack(
            test_redacted_instance.pixel_array
        ).tolist()
        box_color_pixels_original = len(
            np.unique(
                np.where(np.array(list_of_RGB_pixels_original) == mock_box_color)[0]
            )
        )
        box_color_pixels_redacted = len(
            np.unique(
                np.where(np.array(list_of_RGB_pixels_redacted) == mock_box_color)[0]
            )
        )
        mock_set_bbox_color.call_count == 1

    assert box_color_pixels_redacted > box_color_pixels_original
