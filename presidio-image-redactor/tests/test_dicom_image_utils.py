"""Test suite for dicom_image_utils.py"""
from pathlib import Path
import numpy as np
import tempfile
import os
import pydicom
from PIL import Image
from typing import Union, Tuple
import pytest
from presidio_image_redactor.utils.dicom_image_utils import (
    get_all_dcm_files,
    check_if_greyscale,
    rescale_dcm_pixel_array,
    convert_dcm_to_png,
    get_bg_color,
    get_most_common_pixel_value,
    add_padding,
    copy_files_for_processing,
)

TEST_DICOM_PARENT_DIR = "presidio-image-redactor/tests/test_data"
TEST_DICOM_DIR_1 = "presidio-image-redactor/tests/test_data/dicom_dir_1"
TEST_DICOM_DIR_2 = "presidio-image-redactor/tests/test_data/dicom_dir_1/dicom_dir_2"
TEST_DICOM_DIR_3 = "presidio-image-redactor/tests/test_data/dicom_dir_1/dicom_dir_3"
TEST_NUMPY_DIR = "presidio-image-redactor/tests/test_data/numpy_arrays"
TEST_PNG_DIR = "presidio-image-redactor/tests/test_data/png_images"

# ------------------------------------------------------
# get_all_dcm_files()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "dcm_dir, expected_list",
    [
        (
            Path(TEST_DICOM_PARENT_DIR),
            [
                Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"),
                Path(TEST_DICOM_PARENT_DIR, "RGB_ORIGINAL.dcm"),
                Path(TEST_DICOM_DIR_2, "1_ORIGINAL.DCM"),
                Path(TEST_DICOM_DIR_2, "2_ORIGINAL.dicom"),
                Path(TEST_DICOM_DIR_3, "3_ORIGINAL.DICOM"),
            ],
        ),
        (
            Path(TEST_DICOM_DIR_1),
            [
                Path(TEST_DICOM_DIR_2, "1_ORIGINAL.DCM"),
                Path(TEST_DICOM_DIR_2, "2_ORIGINAL.dicom"),
                Path(TEST_DICOM_DIR_3, "3_ORIGINAL.DICOM"),
            ],
        ),
        (
            Path(TEST_DICOM_DIR_2),
            [
                Path(TEST_DICOM_DIR_2, "1_ORIGINAL.DCM"),
                Path(TEST_DICOM_DIR_2, "2_ORIGINAL.dicom"),
            ],
        ),
        (
            Path(TEST_DICOM_DIR_3),
            [
                Path(TEST_DICOM_DIR_3, "3_ORIGINAL.DICOM"),
            ],
        ),
    ],
)
def test_get_all_dcm_files_happy_path(dcm_dir: Path, expected_list: list):
    """Test happy path for get_all_dcm_files

    Args:
        dcm_dir (pathlib.Path): Path to a directory containing at least one .dcm file.
        expected_list (list): List of pathlib Path objects.
    """
    # Arrange

    # Act
    test_files = get_all_dcm_files(dcm_dir)

    # Assert
    assert test_files == expected_list


# ------------------------------------------------------
# check_if_greyscale()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "dcm_file, expected_result",
    [
        (Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"), True),
        (Path(TEST_DICOM_PARENT_DIR, "RGB_ORIGINAL.dcm"), False),
    ],
)
def test_check_if_greyscale_happy_path(dcm_file: Path, expected_result: bool):
    """Test happy path for check_if_greyscale

    Args:
        dcm_file (pathlib.Path): Path to a DICOM file.
        expected_result (bool): Expected output of check_if_greyscale.
    """
    # Arrange
    test_instance = pydicom.dcmread(dcm_file)

    # Act
    test_is_greyscale = check_if_greyscale(test_instance)

    # Assert
    assert test_is_greyscale == expected_result


# ------------------------------------------------------
# rescale_dcm_pixel_array()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "dcm_file, is_greyscale",
    [
        (Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"), True),
        (Path(TEST_DICOM_PARENT_DIR, "RGB_ORIGINAL.dcm"), False),
        (Path(TEST_DICOM_DIR_2, "1_ORIGINAL.DCM"), True),
        (Path(TEST_DICOM_DIR_2, "2_ORIGINAL.dicom"), True),
        (Path(TEST_DICOM_DIR_3, "3_ORIGINAL.DICOM"), True),
    ],
)
def test_check_if_greyscale_happy_path(dcm_file: Path, is_greyscale: bool):
    """Test happy path for rescale_dcm_pixel_array

    Args:
        dcm_file (pathlib.Path): Path to a DICOM file.
        is_greyscale (bool): If loaded DICOM image is greyscale or not.
    """
    # Arrange
    test_instance = pydicom.dcmread(dcm_file)
    test_original_image = test_instance.pixel_array

    # Act
    test_scaled_image = rescale_dcm_pixel_array(test_instance, is_greyscale)

    # Assert
    assert np.shape(test_original_image) == np.shape(test_scaled_image)
    assert np.min(test_scaled_image) >= 0
    assert np.max(test_scaled_image) <= 255
    if is_greyscale is True:
        assert np.max(test_original_image) != np.max(test_scaled_image)
        assert len(np.shape(test_scaled_image)) == 2
    else:
        assert len(np.shape(test_scaled_image)) == 3


# ------------------------------------------------------
# convert_dcm_to_png()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "dcm_file, is_greyscale, rescaled_image_numpy_path",
    [
        (Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"), True, Path(TEST_NUMPY_DIR, "0_ORIGINAL.npy")),
        (Path(TEST_DICOM_PARENT_DIR, "RGB_ORIGINAL.dcm"), False, Path(TEST_NUMPY_DIR, "RGB_ORIGINAL.npy")),
        (Path(TEST_DICOM_DIR_2, "1_ORIGINAL.DCM"), True, Path(TEST_NUMPY_DIR, "1_ORIGINAL.npy")),
        (Path(TEST_DICOM_DIR_2, "2_ORIGINAL.dicom"), True, Path(TEST_NUMPY_DIR, "2_ORIGINAL.npy")),
        (Path(TEST_DICOM_DIR_3, "3_ORIGINAL.DICOM"), True, Path(TEST_NUMPY_DIR, "3_ORIGINAL.npy")),
    ],
)
def test_convert_dcm_to_png_happy_path(mocker, dcm_file: Path, is_greyscale: bool, rescaled_image_numpy_path: Path):
    """Test happy path for convert_dcm_to_png

    Args:
        dcm_file (pathlib.Path): Path to a DICOM file.
        is_greyscale (bool): If loaded DICOM image is greyscale or not.
        rescaled_image_numpy_path (pathlib.Path): Path to file containing numpy array of rescaled image.
    """
    # Arrange
    test_instance = pydicom.dcmread(dcm_file)
    with open(rescaled_image_numpy_path, "rb") as f:
        loaded_numpy_array = np.load(f)

    mock_check_if_gresycale = mocker.patch(
        "presidio_image_redactor.utils.dicom_image_utils.check_if_greyscale", return_value=is_greyscale
    )
    mock_rescale_dcm_pixel_array = mocker.patch(
        "presidio_image_redactor.utils.dicom_image_utils.rescale_dcm_pixel_array",
        return_value=loaded_numpy_array,
    )

    with tempfile.TemporaryDirectory() as tmpdirname:
        # Act
        test_shape, _ = convert_dcm_to_png(dcm_file, tmpdirname)

        # Assert
        mock_check_if_gresycale.call_count == 1
        mock_rescale_dcm_pixel_array.call_count == 1
        assert np.shape(test_instance.pixel_array) == test_shape
        assert f"{dcm_file.stem}.png" in os.listdir(tmpdirname)


# ------------------------------------------------------
# get_bg_color()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "png_file, is_greyscale, invert_flag, expected_bg_color",
    [
        (Path(TEST_PNG_DIR, "0_ORIGINAL.png"), True, False, 243),
        (Path(TEST_PNG_DIR, "RGB_ORIGINAL.png"), False, False, (0, 0, 0)),
        (Path(TEST_PNG_DIR, "1_ORIGINAL.png"), True, False, 0),
        (Path(TEST_PNG_DIR, "2_ORIGINAL.png"), True, False, 0),
        (Path(TEST_PNG_DIR, "3_ORIGINAL.png"), True, False, 0),
        (Path(TEST_PNG_DIR, "0_ORIGINAL.png"), True, True, 12),
        (Path(TEST_PNG_DIR, "RGB_ORIGINAL.png"), False, True, (255, 255, 255)),
        (Path(TEST_PNG_DIR, "1_ORIGINAL.png"), True, True, 255),
        (Path(TEST_PNG_DIR, "2_ORIGINAL.png"), True, True, 255),
        (Path(TEST_PNG_DIR, "3_ORIGINAL.png"), True, True, 255),
    ],
)
def test_get_bg_color_happy_path(
    png_file: Path, is_greyscale: bool, invert_flag: bool, expected_bg_color: Union[int, Tuple[int, int, int]]
):
    """Test happy path for get_bg_color

    Args:
        png_file (pathlib.Path): Path to a PNG file.
        is_greyscale (bool): If loaded DICOM image is greyscale or not.
        invert_flag (bool): True if we want to invert image colors to get foreground.
        expected_bg_color (int or Tuple of int): The expected background color of the image.
    """
    # Arrange
    test_image = Image.open(png_file)

    # Act
    test_bg_color = get_bg_color(test_image, is_greyscale, invert_flag)

    # Assert
    assert test_bg_color == expected_bg_color


# ------------------------------------------------------
# get_most_common_pixel_value()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "dcm_file, box_color_setting, expected_color",
    [
        (Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"), "contrast", 50),
        (Path(TEST_DICOM_DIR_2, "1_ORIGINAL.DCM"), "contrast", 16383),
        (Path(TEST_DICOM_DIR_2, "2_ORIGINAL.dicom"), "contrast", 32767),
        (Path(TEST_DICOM_DIR_3, "3_ORIGINAL.DICOM"), "contrast", 4095),
        (Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"), "background", 973),
        (Path(TEST_DICOM_DIR_2, "1_ORIGINAL.DCM"), "background", 0),
        (Path(TEST_DICOM_DIR_2, "2_ORIGINAL.dicom"), "background", 0),
        (Path(TEST_DICOM_DIR_3, "3_ORIGINAL.DICOM"), "background", 0),
    ],
)
def test_get_most_common_pixel_value_happy_path(
    dcm_file: Path, box_color_setting: str, expected_color: Union[int, Tuple[int, int, int]]
):
    """Test happy path for get_most_common_pixel_value

    Args:
        dcm_file (pathlib.Path): Path to a DICOM file.
        box_color_setting (str): Color setting to use ("contrast" or "background").
        expected_color (int or Tuple of int): The expected color returned for the image.
    """
    # Arrange
    test_instance = pydicom.dcmread(dcm_file)

    # Act
    test_color = get_most_common_pixel_value(test_instance, box_color_setting)

    # Assert
    assert test_color == expected_color


@pytest.mark.parametrize(
    "dcm_file, expected_error_type",
    [
        (Path(TEST_DICOM_PARENT_DIR, "RGB_ORIGINAL.dcm"), "TypeError"),
    ],
)
def test_get_most_common_pixel_value_exceptions(dcm_file: Path, expected_error_type: str):
    """Test error handling of get_most_common_pixel_value

    Args:
        dcm_file (pathlib.Path): Path to a DICOM file.
        expected_error_type (str): Type of error we expect to be raised.
    """
    with pytest.raises(Exception) as exc_info:
        # Arrange
        test_instance = pydicom.dcmread(dcm_file)

        # Act
        _ = get_most_common_pixel_value(test_instance, "contrast")

        # Assert
        assert expected_error_type == exc_info.typename


# ------------------------------------------------------
# add_padding()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "png_file, is_greyscale, padding_width",
    [
        (Path(TEST_PNG_DIR, "0_ORIGINAL.png"), True, 15),
        (Path(TEST_PNG_DIR, "RGB_ORIGINAL.png"), False, 15),
        (Path(TEST_PNG_DIR, "1_ORIGINAL.png"), True, 15),
        (Path(TEST_PNG_DIR, "2_ORIGINAL.png"), True, 15),
        (Path(TEST_PNG_DIR, "3_ORIGINAL.png"), True, 15),
        (Path(TEST_PNG_DIR, "0_ORIGINAL.png"), True, 30),
        (Path(TEST_PNG_DIR, "0_ORIGINAL.png"), True, 99),
    ],
)
def test_add_padding_happy_path(png_file: Path, is_greyscale: bool, padding_width: int):
    """Test happy path for add_padding

    Args:
        png_file (pathlib.Path): Path to a PNG file.
        is_greyscale (bool): If loaded DICOM image is greyscale or not.
        padding_width (int): Pixel width of padding (uniform).
    """
    # Arrange
    test_image = Image.open(png_file)

    # Act
    test_image_with_padding = add_padding(test_image, is_greyscale, padding_width)

    # Assert
    assert test_image_with_padding.height - test_image.height == 2 * padding_width
    assert test_image_with_padding.width - test_image.width == 2 * padding_width


@pytest.mark.parametrize(
    "png_file, is_greyscale, padding_width, expected_error_type",
    [
        (Path(TEST_PNG_DIR, "0_ORIGINAL.png"), True, -1, "ValueError"),
        (Path(TEST_PNG_DIR, "0_ORIGINAL.png"), True, 0, "ValueError"),
        (Path(TEST_PNG_DIR, "0_ORIGINAL.png"), True, 200, "ValueError"),
    ],
)
def test_add_padding_exceptions(png_file: Path, is_greyscale: bool, padding_width: int, expected_error_type: str):
    """Test error handling of add_padding

    Args:
        png_file (pathlib.Path): Path to a PNG file.
        is_greyscale (bool): If loaded DICOM image is greyscale or not.
        padding_width (int): Pixel width of padding (uniform).
        expected_error_type (str): Type of error we expect to be raised.
    """
    with pytest.raises(Exception) as exc_info:
        # Arrange
        test_image = Image.open(png_file)

        # Act
        _, _ = add_padding(test_image, is_greyscale, padding_width)

    # Assert
    assert expected_error_type == exc_info.typename


# ------------------------------------------------------
# copy_files_for_processing()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "src_path, expected_num_of_files",
    [
        (Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"), 1),
        (Path(TEST_DICOM_PARENT_DIR), 15),
        (Path(TEST_DICOM_DIR_1), 3),
        (Path(TEST_DICOM_DIR_2), 2),
        (Path(TEST_DICOM_DIR_3), 1),
        (Path(TEST_PNG_DIR), 5),
        (Path(TEST_NUMPY_DIR), 5),
    ],
)
def test_copy_files_for_processing_happy_path(src_path: Path, expected_num_of_files: int):
    """Test happy path for copy_files_for_processing

    Args:
        src_path (pathlib.Path): Path to a file or directory to copy.
        expected_num_of_files (int): Expected number of files to be copied.
    """
    # Arrange

    with tempfile.TemporaryDirectory() as tmpdirname:
        # Act
        test_dst_path = copy_files_for_processing(src_path, tmpdirname)

        # Arrange
        p = Path(tmpdirname).glob(f"**/*")
        files = [x for x in p if x.is_file()]

        # Assert
        assert Path(tmpdirname) < test_dst_path
        assert expected_num_of_files == len(files)
