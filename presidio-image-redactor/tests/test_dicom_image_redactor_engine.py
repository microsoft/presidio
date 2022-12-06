"""Test suite for dicom_image_redactor_engine.py"""
from pathlib import Path
import tempfile
import os
import numpy as np
from PIL import Image
import pydicom
from presidio_image_redactor.dicom_image_redactor_engine import DicomImageRedactorEngine
from presidio_image_redactor.entities.image_recognizer_result import (
    ImageRecognizerResult,
)
from typing import Union, Tuple
import pytest


TEST_DICOM_PARENT_DIR = "presidio-image-redactor/tests/test_data"
TEST_DICOM_DIR_1 = "presidio-image-redactor/tests/test_data/dicom_dir_1"
TEST_DICOM_DIR_2 = "presidio-image-redactor/tests/test_data/dicom_dir_1/dicom_dir_2"
TEST_DICOM_DIR_3 = "presidio-image-redactor/tests/test_data/dicom_dir_1/dicom_dir_3"
TEST_NUMPY_DIR = "presidio-image-redactor/tests/test_data/numpy_arrays"
TEST_PNG_DIR = "presidio-image-redactor/tests/test_data/png_images"


@pytest.fixture(scope="module")
def mock_engine():
    """Instance of the DicomImageRedactorEngine"""
    # Arrange

    # Act
    dicom_image_redactor_engine = DicomImageRedactorEngine()

    return dicom_image_redactor_engine


# ------------------------------------------------------
# DicomImageRedactorEngine._get_all_dcm_files()
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
def test_get_all_dcm_files_happy_path(
    mock_engine: DicomImageRedactorEngine, dcm_dir: Path, expected_list: list
):
    """Test happy path for DicomImageRedactorEngine._get_all_dcm_files

    Args:
        dcm_dir (pathlib.Path): Path to a directory containing at least one .dcm file.
        expected_list (list): List of pathlib Path objects.
    """
    # Arrange

    # Act
    test_files = mock_engine._get_all_dcm_files(dcm_dir)

    # Assert
    assert test_files == expected_list


# ------------------------------------------------------
# DicomImageRedactorEngine._check_if_greyscale()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "dcm_file, expected_result",
    [
        (Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"), True),
        (Path(TEST_DICOM_PARENT_DIR, "RGB_ORIGINAL.dcm"), False),
    ],
)
def test_check_if_greyscale_happy_path(
    mock_engine: DicomImageRedactorEngine, dcm_file: Path, expected_result: bool
):
    """Test happy path for DicomImageRedactorEngine._check_if_greyscale

    Args:
        dcm_file (pathlib.Path): Path to a DICOM file.
        expected_result (bool): Expected output of _check_if_greyscale.
    """
    # Arrange
    test_instance = pydicom.dcmread(dcm_file)

    # Act
    test_is_greyscale = mock_engine._check_if_greyscale(test_instance)

    # Assert
    assert test_is_greyscale == expected_result


# ------------------------------------------------------
# DicomImageRedactorEngine._rescale_dcm_pixel_array()
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
def test_check_if_greyscale_happy_path(
    mock_engine: DicomImageRedactorEngine, dcm_file: Path, is_greyscale: bool
):
    """Test happy path for DicomImageRedactorEngine._rescale_dcm_pixel_array

    Args:
        dcm_file (pathlib.Path): Path to a DICOM file.
        is_greyscale (bool): If loaded DICOM image is greyscale or not.
    """
    # Arrange
    test_instance = pydicom.dcmread(dcm_file)
    test_original_image = test_instance.pixel_array

    # Act
    test_scaled_image = mock_engine._rescale_dcm_pixel_array(
        test_instance, is_greyscale
    )

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
# DicomImageRedactorEngine._save_pixel_array_as_png()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "dcm_file, is_greyscale, rescaled_image_numpy_path",
    [
        (
            Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"),
            True,
            Path(TEST_NUMPY_DIR, "0_ORIGINAL.npy"),
        ),
        (
            Path(TEST_DICOM_PARENT_DIR, "RGB_ORIGINAL.dcm"),
            False,
            Path(TEST_NUMPY_DIR, "RGB_ORIGINAL.npy"),
        ),
        (
            Path(TEST_DICOM_DIR_2, "1_ORIGINAL.DCM"),
            True,
            Path(TEST_NUMPY_DIR, "1_ORIGINAL.npy"),
        ),
        (
            Path(TEST_DICOM_DIR_2, "2_ORIGINAL.dicom"),
            True,
            Path(TEST_NUMPY_DIR, "2_ORIGINAL.npy"),
        ),
        (
            Path(TEST_DICOM_DIR_3, "3_ORIGINAL.DICOM"),
            True,
            Path(TEST_NUMPY_DIR, "3_ORIGINAL.npy"),
        ),
    ],
)
def test_save_pixel_array_as_png_happy_path(
    mock_engine: DicomImageRedactorEngine,
    dcm_file: Path,
    is_greyscale: bool,
    rescaled_image_numpy_path: Path,
):
    """Test happy path for DicomImageRedactorEngine._save_pixel_array_as_png

    Args:
        dcm_file (pathlib.Path): Path to a DICOM file.
        is_greyscale (bool): If loaded DICOM image is greyscale or not.
        rescaled_image_numpy_path (pathlib.Path): Path to file containing numpy array of rescaled image.
    """
    # Arrange
    test_instance = pydicom.dcmread(dcm_file)
    test_image = mock_engine._rescale_dcm_pixel_array(test_instance, is_greyscale)
    filename = "test"
    with open(rescaled_image_numpy_path, "rb") as f:
        loaded_numpy_array = np.load(f)

    with tempfile.TemporaryDirectory() as tmpdirname:
        # Act
        _ = mock_engine._save_pixel_array_as_png(
            test_image, is_greyscale, filename, tmpdirname
        )

        # Assert
        assert np.shape(test_image) == np.shape(loaded_numpy_array)
        assert f"{filename}.png" in os.listdir(tmpdirname)


# ------------------------------------------------------
# DicomImageRedactorEngine._convert_dcm_to_png()
# ------------------------------------------------------
def test_convert_dcm_to_png_happy_path(mocker):
    """Test happy path for DicomImageRedactorEngine._convert_dcm_to_png"""
    # Arrange
    mock_dcm_read = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.pydicom.dcmread",
        return_value=None,
    )
    mock_check_if_gresycale = mocker.patch.object(
        DicomImageRedactorEngine,
        "_check_if_greyscale",
        return_value=True,
    )
    mock_rescale_dcm_pixel_array = mocker.patch.object(
        DicomImageRedactorEngine,
        "_rescale_dcm_pixel_array",
        return_value=np.array([1, 2, 3]),
    )
    mock_save_array_as_png = mocker.patch.object(
        DicomImageRedactorEngine, "_save_pixel_array_as_png", return_value=None
    )
    mock_engine = DicomImageRedactorEngine()

    with tempfile.TemporaryDirectory() as tmpdirname:
        # Act
        _, _ = mock_engine._convert_dcm_to_png(Path("filename.dcm"), tmpdirname)

        # Assert
        assert mock_dcm_read.call_count == 1
        assert mock_check_if_gresycale.call_count == 1
        assert mock_rescale_dcm_pixel_array.call_count == 1
        assert mock_save_array_as_png.call_count == 1


# ------------------------------------------------------
# DicomImageRedactorEngine._get_bg_color()
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
    mock_engine: DicomImageRedactorEngine,
    png_file: Path,
    is_greyscale: bool,
    invert_flag: bool,
    expected_bg_color: Union[int, Tuple[int, int, int]],
):
    """Test happy path for DicomImageRedactorEngine._get_bg_color

    Args:
        png_file (pathlib.Path): Path to a PNG file.
        is_greyscale (bool): If loaded DICOM image is greyscale or not.
        invert_flag (bool): True if we want to invert image colors to get foreground.
        expected_bg_color (int or Tuple of int): The expected background color of the image.
    """
    # Arrange
    test_image = Image.open(png_file)

    # Act
    test_bg_color = mock_engine._get_bg_color(test_image, is_greyscale, invert_flag)

    # Assert
    assert test_bg_color == expected_bg_color


# ------------------------------------------------------
# DicomImageRedactorEngine._get_most_common_pixel_value()
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
    mock_engine: DicomImageRedactorEngine,
    dcm_file: Path,
    box_color_setting: str,
    expected_color: Union[int, Tuple[int, int, int]],
):
    """Test happy path for DicomImageRedactorEngine._get_most_common_pixel_value

    Args:
        dcm_file (pathlib.Path): Path to a DICOM file.
        box_color_setting (str): Color setting to use ("contrast" or "background").
        expected_color (int or Tuple of int): The expected color returned for the image.
    """
    # Arrange
    test_instance = pydicom.dcmread(dcm_file)

    # Act
    test_color = mock_engine._get_most_common_pixel_value(
        test_instance, box_color_setting
    )

    # Assert
    assert test_color == expected_color


@pytest.mark.parametrize(
    "dcm_file, expected_error_type",
    [
        (Path(TEST_DICOM_PARENT_DIR, "RGB_ORIGINAL.dcm"), "TypeError"),
    ],
)
def test_get_most_common_pixel_value_exceptions(
    mock_engine: DicomImageRedactorEngine, dcm_file: Path, expected_error_type: str
):
    """Test error handling of _get_most_common_pixel_value

    Args:
        dcm_file (pathlib.Path): Path to a DICOM file.
        expected_error_type (str): Type of error we expect to be raised.
    """
    with pytest.raises(Exception) as exc_info:
        # Arrange
        test_instance = pydicom.dcmread(dcm_file)

        # Act
        _ = mock_engine._get_most_common_pixel_value(test_instance, "contrast")

        # Assert
        assert expected_error_type == exc_info.typename


# ------------------------------------------------------
# DicomImageRedactorEngine._add_padding()
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
def test_add_padding_happy_path(
    mock_engine: DicomImageRedactorEngine,
    png_file: Path,
    is_greyscale: bool,
    padding_width: int,
):
    """Test happy path for DicomImageRedactorEngine._add_padding

    Args:
        png_file (pathlib.Path): Path to a PNG file.
        is_greyscale (bool): If loaded DICOM image is greyscale or not.
        padding_width (int): Pixel width of padding (uniform).
    """
    # Arrange
    test_image = Image.open(png_file)

    # Act
    test_image_with_padding = mock_engine._add_padding(
        test_image, is_greyscale, padding_width
    )

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
def test_add_padding_exceptions(
    mock_engine: DicomImageRedactorEngine,
    png_file: Path,
    is_greyscale: bool,
    padding_width: int,
    expected_error_type: str,
):
    """Test error handling of _add_padding

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
        _, _ = mock_engine._add_padding(test_image, is_greyscale, padding_width)

    # Assert
    assert expected_error_type == exc_info.typename


# ------------------------------------------------------
# DicomImageRedactorEngine._copy_files_for_processing()
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
def test_copy_files_for_processing_happy_path(
    mock_engine: DicomImageRedactorEngine, src_path: Path, expected_num_of_files: int
):
    """Test happy path for DicomImageRedactorEngine._copy_files_for_processing

    Args:
        src_path (pathlib.Path): Path to a file or directory to copy.
        expected_num_of_files (int): Expected number of files to be copied.
    """
    # Arrange

    with tempfile.TemporaryDirectory() as tmpdirname:
        # Act
        test_dst_path = mock_engine._copy_files_for_processing(src_path, tmpdirname)

        # Arrange
        p = Path(tmpdirname).glob(f"**/*")
        files = [x for x in p if x.is_file()]

        # Assert
        assert Path(tmpdirname) < test_dst_path
        assert expected_num_of_files == len(files)


# ------------------------------------------------------
# DicomImageRedactorEngine._get_text_metadata()
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
    mock_engine: DicomImageRedactorEngine,
    dcm_path: Path,
    metadata_text_len: int,
    is_name_true_len: int,
    is_patient_true_len: int,
):
    """Test happy path for DicomImageRedactorEngine._get_text_metadata

    Args:
        dcm_path (pathlib.Path): Path to DICOM file.
        metadata_text_len (int): Length of the expected returned metadata_text list.
        is_name_true_len (int): Number of true values in the returned is_name list.
        is_patient_true_len (int): Number of true values in the returned is_name list.
    """
    # Arrange
    test_instance = pydicom.dcmread(dcm_path)

    # Act
    test_metadata_text, test_is_name, test_is_patient = mock_engine._get_text_metadata(
        test_instance
    )

    # Assert
    idx_is_name = list(np.where(np.array(test_is_name) == True)[0])
    idx_is_patient = list(np.where(np.array(test_is_patient) == True)[0])

    assert len(test_metadata_text) == len(test_is_name) == len(test_is_patient)
    assert len(idx_is_name) == is_name_true_len
    assert len(idx_is_patient) == is_patient_true_len
    assert type(test_metadata_text[idx_is_name[0]]) == str


# ------------------------------------------------------
# DicomImageRedactorEngine._process_names()
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
    mock_engine: DicomImageRedactorEngine,
    text_metadata: list,
    is_name: list,
    expected_phi_list: list,
):
    """Test happy path for DicomImageRedactorEngine._process_names

    Args:
        text_metadata (list): List of text metadata.
        is_name (list): Whether each element is a name or not.
        expected_phi_list (list): List of expected output.
    """
    # Arrange

    # Act
    test_phi_list = mock_engine._process_names(text_metadata, is_name)

    # Assert
    assert set(test_phi_list) == set(expected_phi_list)


# ------------------------------------------------------
# DicomImageRedactorEngine._add_known_generic_phi()
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
def test_add_known_generic_phi_happy_path(
    mock_engine: DicomImageRedactorEngine, phi_list: list, expected_return_list: list
):
    """Test happy path for DicomImageRedactorEngine._add_known_generic_phi

    Args:
        phi_list (list): List of PHI.
        expected_return_list (list): List of expected output.
    """
    # Arrange

    # Act
    test_phi_list = mock_engine._add_known_generic_phi(phi_list)

    # Assert
    assert set(test_phi_list) == set(expected_return_list)


# ------------------------------------------------------
# DicomImageRedactorEngine._make_phi_list()
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
    mock_engine: DicomImageRedactorEngine,
    original_metadata: list,
    mock_process_names_val: list,
    mock_add_known_val: list,
    expected_return_list: list,
):
    """Test happy path for DicomImageRedactorEngine._make_phi_list

    Args:
        original_metadata (list): List extracted metadata (excluding pixel array).
        mock_process_names_val (list): Value to provide to mock process_names.
        mock_add_known_val (list): Value to provide to mock _add_known_generic_phi.
        expected_return_list (list): List of expected output.
    """
    # Arrange
    mock_process_names = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._process_names",
        return_value=mock_process_names_val,
    )
    mock_add_known_generic_phi = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._add_known_generic_phi",
        return_value=mock_add_known_val,
    )

    # Act
    test_phi_str_list = mock_engine._make_phi_list(original_metadata, [], [])

    # Assert
    assert mock_process_names.call_count == 1
    assert mock_add_known_generic_phi.call_count == 1
    assert set(test_phi_str_list) == set(expected_return_list)


# ------------------------------------------------------
# DicomImageRedactorEngine._get_bboxes_from_analyzer_results()
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
    mock_engine: DicomImageRedactorEngine,
    analyzer_results: list,
    expected_bboxes_dict: dict,
):
    """Test happy path for DicomImageRedactorEngine._get_bboxes_from_analyzer_results

    Args:
        analyzer_results (list): Results from using ImageAnalyzerEngine.
        expected_bboxes_dict (dict): Expected output bounding box dictionary.
    """
    # Arrange

    # Act
    test_bboxes_dict = mock_engine._get_bboxes_from_analyzer_results(analyzer_results)

    # Assert
    assert test_bboxes_dict == expected_bboxes_dict


# ------------------------------------------------------
# DicomImageRedactorEngine._format_bboxes()
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
    mocker,
    mock_engine: DicomImageRedactorEngine,
    mock_intermediate_bbox: dict,
    padding_width: int,
    expected_bboxes_dict: dict,
):
    """Test happy path for DicomImageRedactorEngine._format_bboxes

    Args:
        mock_intermediate_bbox (dict): Value for mock of _get_bboxes_from_analyzer_results.
        padding_width (int): Pixel width used for padding.
        expected_bboxes_dict (dict): Expected output bounding box dictionary.
    """
    # Arrange
    mock_get_bboxes = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._get_bboxes_from_analyzer_results",
        return_value=mock_intermediate_bbox,
    )

    # Act
    test_bboxes_dict = mock_engine._format_bboxes([], padding_width)

    # Assert
    assert mock_get_bboxes.call_count == 1
    assert test_bboxes_dict == expected_bboxes_dict


@pytest.mark.parametrize(
    "padding_width, expected_error_type",
    [(-1, "ValueError"), (-200, "ValueError")],
)
def test_format_bboxes_exceptions(
    mock_engine: DicomImageRedactorEngine, padding_width: int, expected_error_type: str
):
    """Test error handling of _format_bboxes

    Args:
        padding_width (int): Pixel width used for padding.
        expected_error_type (str): Type of error we expect to be raised.
    """
    with pytest.raises(Exception) as exc_info:
        # Act
        _ = mock_engine._format_bboxes([], padding_width)

    # Assert
    assert expected_error_type == exc_info.typename


# ------------------------------------------------------
# DicomImageRedactorEngine._set_bbox_color()
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
    mocker,
    box_color_setting: str,
    mock_box_color: Union[int, Tuple[int, int, int]],
):
    """Test happy path for DicomImageRedactorEngine._set_bbox_color

    Args:
        box_color_setting (str): Determines how box color is selected.
        mock_box_color (int or Tuple of int): Color value to assign to mocker.
    """
    # Arrange
    test_instance = pydicom.dcmread(Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"))

    mock_convert_dcm_to_png = mocker.patch.object(
        DicomImageRedactorEngine, "_convert_dcm_to_png", return_value=[None, True]
    )
    mock_Image_open = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.Image.open",
        return_value=None,
    )
    mock_get_bg_color = mocker.patch.object(
        DicomImageRedactorEngine,
        "_get_bg_color",
        return_value=mock_box_color,
    )
    mock_engine = DicomImageRedactorEngine()

    # Act
    test_box_color = mock_engine._set_bbox_color(test_instance, box_color_setting)

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
def test_set_bbox_color_exceptions(
    mock_engine: DicomImageRedactorEngine,
    box_color_setting: str,
    expected_error_type: str,
):
    """Test error handling of _set_bbox_color

    Args:
        box_color_setting (str): Determines how box color is selected.
        expected_error_type (str): Type of error we expect to be raised.
    """
    with pytest.raises(Exception) as exc_info:
        # Arrange
        test_instance = pydicom.dcmread(Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"))

        # Act
        _ = mock_engine._set_bbox_color(test_instance, box_color_setting)

    # Assert
    assert expected_error_type == exc_info.typename


# ------------------------------------------------------
# DicomImageRedactorEngine._add_redact_box()
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
    """Test happy path for DicomImageRedactorEngine._add_redact_box

    Args:
        dcm_path (pathlib.Path): Path to DICOM file.
        mock_is_greyscale (bool): Value to use when mocking _check_if_greyscale.
        mock_box_color (int or Tuple of int): Color value to assign to mocker.
        bouding_boxes_coordinates (dict): Formatted bbox coordinates.
    """
    # Arrange
    test_instance = pydicom.dcmread(dcm_path)
    mock_check_if_greyscale = mocker.patch.object(
        DicomImageRedactorEngine,
        "_check_if_greyscale",
        return_value=mock_is_greyscale,
    )
    mock_get_common_pixel = mocker.patch.object(
        DicomImageRedactorEngine,
        "_get_most_common_pixel_value",
        return_value=mock_box_color,
    )
    mock_set_bbox_color = mocker.patch.object(
        DicomImageRedactorEngine,
        "_set_bbox_color",
        return_value=mock_box_color,
    )
    mock_engine = DicomImageRedactorEngine()

    # Act
    test_redacted_instance = mock_engine._add_redact_box(
        test_instance, bounding_boxes_coordinates
    )

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


# ------------------------------------------------------
# DicomImageRedactorEngine _validate_paths()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "input_path, output_dir",
    [
        (".", "."),
        (TEST_DICOM_PARENT_DIR, "output"),
        (str(Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm")), "output"),
        (TEST_DICOM_DIR_1, "output"),
        (TEST_DICOM_DIR_2, "output"),
        (TEST_DICOM_DIR_3, "output"),
    ],
)
def test_DicomImageRedactorEngine_validate_paths_happy_path(
    mock_engine: DicomImageRedactorEngine,
    input_path: str,
    output_dir: str,
):
    """Test happy path for DicomImageRedactorEngine _validate_paths()

    Args:
        mock_engine (DicomImageRedactorEngine): DicomImageRedactorEngine object.
        input_path (str): Path to input DICOM file or dir.
        output_dir (str): Path to parent directory to write output to.
    """
    try:
        # Act and Assert
        mock_engine._validate_paths(input_path, output_dir)

    except Exception as exc:
        assert False, f"'_validate_paths' raised an exception {exc}"


@pytest.mark.parametrize(
    "input_path, output_dir, expected_error_type",
    [
        (".", str(Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm")), "TypeError"),
        ("nonexistentfile.extension", ".", "TypeError"),
    ],
)
def test_DicomImageRedactorEngine_validate_paths_exceptions(
    mock_engine: DicomImageRedactorEngine,
    input_path: str,
    output_dir: str,
    expected_error_type: str,
):
    """Test error handling of DicomImageRedactorEngine _validate_paths()

    Args:
        mock_engine (DicomImageRedactorEngine): DicomImageRedactorEngine object.
        input_path (str): Path to input DICOM file or dir.
        output_dir (str): Path to parent directory to write output to.
        expected_error_type (str): Type of error we expect to be raised.
    """
    with pytest.raises(Exception) as exc_info:
        # Act
        mock_engine._validate_paths(input_path, output_dir)

    # Assert
    assert expected_error_type == exc_info.typename


# ------------------------------------------------------
# DicomImageRedactorEngine redact()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "dcm_path",
    [
        (Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm")),
        (Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm")),
        (Path(TEST_DICOM_PARENT_DIR, "RGB_ORIGINAL.dcm")),
        (Path(TEST_DICOM_DIR_2, "1_ORIGINAL.DCM")),
        (Path(TEST_DICOM_DIR_2, "2_ORIGINAL.dicom")),
        (Path(TEST_DICOM_DIR_3, "3_ORIGINAL.DICOM")),
    ],
)
def test_DicomImageRedactorEngine_redact_happy_path(
    mocker,
    mock_engine: DicomImageRedactorEngine,
    dcm_path: str,
):
    """Test happy path for DicomImageRedactorEngine redact()

    Args:
        mock_engine (DicomImageRedactorEngine): DicomImageRedactorEngine object.
        dcm_path (str): Path to input DICOM file or dir.
        output_dir (str): Path to parent directory to write output to.
        overwrite (bool): True if overwriting original files.
    """
    # Arrange
    test_image = pydicom.dcmread(dcm_path)

    mock_check_greyscale = mocker.patch.object(
        DicomImageRedactorEngine,
        "_check_if_greyscale",
        return_value = None
    )
    mock_rescale_dcm = mocker.patch.object(
        DicomImageRedactorEngine,
        "_rescale_dcm_pixel_array",
        return_value = None
    )
    mock_save_pixel_array = mocker.patch.object(
        DicomImageRedactorEngine,
        "_save_pixel_array_as_png",
        return_value = None
    )
    mock_image_open = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.Image.open",
        return_value=None,
    )
    mock_add_padding = mocker.patch.object(
        DicomImageRedactorEngine,
        "_add_padding",
        return_value=None,
    )
    
    mock_get_text_metadata = mocker.patch.object(
        DicomImageRedactorEngine,
        "_get_text_metadata",
        return_value=[None, None, None],
    )
    mock_make_phi_list = mocker.patch.object(
        DicomImageRedactorEngine,
        "_make_phi_list",
        return_value=None,
    )

    mock_pattern_recognizer = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.PatternRecognizer",
        return_value=None,
    )

    mock_analyze = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.ImageAnalyzerEngine.analyze",
        return_value=None,
    )

    mock_format_bboxes = mocker.patch.object(
        DicomImageRedactorEngine,
        "_format_bboxes",
        return_value=None,
    )

    mock_add_redact_box = mocker.patch.object(
        DicomImageRedactorEngine,
        "_add_redact_box",
        return_value=None,
    )

    mock_engine = DicomImageRedactorEngine()

    # Act
    mock_engine.redact(test_image)

    # Assert
    assert mock_check_greyscale.call_count == 1
    assert mock_rescale_dcm.call_count == 1
    assert mock_save_pixel_array.call_count == 1
    assert mock_image_open.call_count == 1
    assert mock_add_padding.call_count == 1
    assert mock_get_text_metadata.call_count == 1
    assert mock_make_phi_list.call_count == 1
    assert mock_pattern_recognizer.call_count == 1
    assert mock_analyze.call_count == 1
    assert mock_format_bboxes.call_count == 1
    assert mock_add_redact_box.call_count == 1


# ------------------------------------------------------
# DicomImageRedactorEngine _redact_single_dicom_image()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "dcm_path, output_dir, overwrite",
    [
        (Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"), "output", False),
        (Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"), "output", True),
        (Path(TEST_DICOM_PARENT_DIR, "RGB_ORIGINAL.dcm"), "output", False),
        (Path(TEST_DICOM_DIR_2, "1_ORIGINAL.DCM"), "output", False),
        (Path(TEST_DICOM_DIR_2, "2_ORIGINAL.dicom"), "output", False),
        (Path(TEST_DICOM_DIR_3, "3_ORIGINAL.DICOM"), "output", False),
    ],
)
def test_DicomImageRedactorEngine_redact_single_dicom_image_happy_path(
    mocker,
    mock_engine: DicomImageRedactorEngine,
    dcm_path: str,
    output_dir: str,
    overwrite: bool,
):
    """Test happy path for DicomImageRedactorEngine _redact_single_dicom_image()

    Args:
        mock_engine (DicomImageRedactorEngine): DicomImageRedactorEngine object.
        dcm_path (str): Path to input DICOM file or dir.
        output_dir (str): Path to parent directory to write output to.
        overwrite (bool): True if overwriting original files.
    """
    # Arrange
    mock_copy_files = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._copy_files_for_processing",
        return_value=dcm_path,
    )
    mock_convert_dcm_to_png = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._convert_dcm_to_png",
        return_value=[None, None],
    )
    mock_image_open = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.Image.open",
        return_value=None,
    )
    mock_add_padding = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._add_padding",
        return_value=None,
    )
    mock_get_text_metadata = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._get_text_metadata",
        return_value=[None, None, None],
    )
    mock_make_phi_list = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._make_phi_list",
        return_value=None,
    )

    mock_pattern_recognizer = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.PatternRecognizer",
        return_value=None,
    )

    mock_analyze = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.ImageAnalyzerEngine.analyze",
        return_value=None,
    )

    mock_format_bboxes = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._format_bboxes",
        return_value=None,
    )

    class MockInstance:
        def save_as(self, dst_path: str):
            return None

    mock_add_redact_box = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._add_redact_box",
        return_value=MockInstance(),
    )

    # Act
    mock_engine._redact_single_dicom_image(
        dcm_path, "contrast", 25, overwrite, output_dir
    )

    # Assert
    if overwrite is True:
        assert mock_copy_files.call_count == 0
    else:
        assert mock_copy_files.call_count == 1
    assert mock_convert_dcm_to_png.call_count == 1
    assert mock_image_open.call_count == 1
    assert mock_add_padding.call_count == 1
    assert mock_get_text_metadata.call_count == 1
    assert mock_make_phi_list.call_count == 1
    assert mock_pattern_recognizer.call_count == 1
    assert mock_analyze.call_count == 1
    assert mock_format_bboxes.call_count == 1
    assert mock_add_redact_box.call_count == 1


@pytest.mark.parametrize(
    "dcm_path, expected_error_type",
    [
        (Path(TEST_DICOM_PARENT_DIR), "FileNotFoundError"),
        (Path("nonexistentfile.extension"), "FileNotFoundError"),
    ],
)
def test_DicomImageRedactorEngine_redact_single_dicom_image_exceptions(
    mock_engine: DicomImageRedactorEngine,
    dcm_path: str,
    expected_error_type: str,
):
    """Test error handling of DicomImageRedactorEngine _redact_single_dicom_image()

    Args:
        mock_engine (DicomImageRedactorEngine): DicomImageRedactorEngine object.
        dcm_path (str): Path to input DICOM file or dir.
        expected_error_type (str): Type of error we expect to be raised.
    """
    with pytest.raises(Exception) as exc_info:
        # Act
        mock_engine._redact_single_dicom_image(dcm_path, "contrast", 25, False, ".")

    # Assert
    assert expected_error_type == exc_info.typename


# ------------------------------------------------------
# DicomImageRedactorEngine _redact_multiple_dicom_images()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "dcm_path, output_dir, overwrite",
    [
        (Path(TEST_DICOM_PARENT_DIR), "output", False),
        (Path(TEST_DICOM_PARENT_DIR), "output", True),
        (Path(TEST_DICOM_DIR_1), "output", False),
        (Path(TEST_DICOM_DIR_2), "output", False),
        (Path(TEST_DICOM_DIR_3), "output", False),
    ],
)
def test_DicomImageRedactorEngine_redact_multiple_dicom_images_happy_path(
    mocker,
    mock_engine: DicomImageRedactorEngine,
    dcm_path: str,
    output_dir: str,
    overwrite: bool,
):
    """Test happy path for DicomImageRedactorEngine _redact_multiple_dicom_images()

    Args:
        mock_engine (DicomImageRedactorEngine): DicomImageRedactorEngine object.
        dcm_path (str): Path to input DICOM file or dir.
        output_dir (str): Path to parent directory to write output to.
        overwrite (bool): True if overwriting original files.
    """
    # Arrange
    mock_copy_files = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._copy_files_for_processing",
        return_value=dcm_path,
    )
    mock_dcm_files = [
        Path("dir1/dir2/file1.dcm"),
        Path("dir1/dir2/file2.dcm"),
        Path("dir1/dir2/dir3/file3.dcm"),
    ]
    mock_get_all_dcm_files = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._get_all_dcm_files",
        return_value=mock_dcm_files,
    )
    mock_redact_single = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._redact_single_dicom_image",
        return_value=None,
    )

    # Act
    mock_engine._redact_multiple_dicom_images(
        dcm_path, "contrast", 25, overwrite, output_dir
    )

    # Assert
    if overwrite is True:
        assert mock_copy_files.call_count == 0
    else:
        assert mock_copy_files.call_count == 1
    assert mock_get_all_dcm_files.call_count == 1
    assert mock_redact_single.call_count == len(mock_dcm_files)


@pytest.mark.parametrize(
    "dcm_path, expected_error_type",
    [
        (Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"), "FileNotFoundError"),
        (Path("nonexistentdir"), "FileNotFoundError"),
    ],
)
def test_DicomImageRedactorEngine_redact_multiple_dicom_images_exceptions(
    mock_engine: DicomImageRedactorEngine,
    dcm_path: str,
    expected_error_type: str,
):
    """Test error handling of DicomImageRedactorEngine _redact_multiple_dicom_images()

    Args:
        mock_engine (DicomImageRedactorEngine): DicomImageRedactorEngine object.
        dcm_path (str): Path to input DICOM file or dir.
        expected_error_type (str): Type of error we expect to be raised.
    """
    with pytest.raises(Exception) as exc_info:
        # Act
        mock_engine._redact_multiple_dicom_images(dcm_path, "contrast", 25, False, ".")

    # Assert
    assert expected_error_type == exc_info.typename


# ------------------------------------------------------
# DicomImageRedactorEngine redact_from_file()
# ------------------------------------------------------
@pytest.mark.parametrize(
    "dcm_path, mock_dst_path, is_dir",
    [
        (TEST_DICOM_PARENT_DIR, Path(TEST_DICOM_PARENT_DIR), True),
        (
            f"{TEST_DICOM_PARENT_DIR}/0_ORIGINAL.dcm",
            Path(TEST_DICOM_PARENT_DIR, "0_ORIGINAL.dcm"),
            False,
        ),
        (TEST_DICOM_DIR_2, Path(TEST_DICOM_DIR_1), True),
        (TEST_DICOM_DIR_2, Path(TEST_DICOM_DIR_2), True),
        (TEST_DICOM_DIR_3, Path(TEST_DICOM_DIR_3), True),
        (
            f"{TEST_DICOM_DIR_3}/3_ORIGINAL.DICOM",
            Path(TEST_DICOM_DIR_3, "3_ORIGINAL.DICOM"),
            False,
        ),
    ],
)
def test_DicomImageRedactorEngine_redact_from_file_happy_path(
    mocker,
    mock_engine: DicomImageRedactorEngine,
    dcm_path: str,
    mock_dst_path: Path,
    is_dir: bool,
):
    """Test happy path for DicomImageRedactorEngine redact_from_file()

    Args:
        mock_engine (DicomImageRedactorEngine): DicomImageRedactorEngine object.
        dcm_path (str): Path to input DICOM file or dir.
        mock_dst_path (pathlib.Path): Path to DICOM dir or file.
        is_dir (bool): Whether mock_dst_path is a directory or file.
    """
    # Arrange
    mock_validate_paths = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._validate_paths",
        return_value=None,
    )
    mock_copy_files = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._copy_files_for_processing",
        return_value=mock_dst_path,
    )
    mock_redact_single = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._redact_single_dicom_image",
        return_value=None,
    )
    mock_redact_multiple = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.DicomImageRedactorEngine._redact_multiple_dicom_images",
        return_value=None,
    )

    # Act
    mock_engine.redact_from_file(dcm_path, "output", 25, "contrast")

    # Assert
    assert mock_validate_paths.call_count == 1
    assert mock_copy_files.call_count == 1
    if is_dir is True:
        assert mock_redact_single.call_count == 0
        assert mock_redact_multiple.call_count == 1
    else:
        assert mock_redact_single.call_count == 1
        assert mock_redact_multiple.call_count == 0
