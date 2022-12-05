"""Test suite for dicom_image_redactor_engine.py"""
from pathlib import Path
from presidio_image_redactor.dicom_image_redactor_engine import DicomImageRedactorEngine
import pytest


TEST_DICOM_PARENT_DIR = "presidio-image-redactor/tests/test_data"
TEST_DICOM_DIR_1 = "presidio-image-redactor/tests/test_data/dicom_dir_1"
TEST_DICOM_DIR_2 = "presidio-image-redactor/tests/test_data/dicom_dir_1/dicom_dir_2"
TEST_DICOM_DIR_3 = "presidio-image-redactor/tests/test_data/dicom_dir_1/dicom_dir_3"


@pytest.fixture(scope="module")
def mock_engine():
    """Instance of the DicomImageRedactorEngine"""
    # Arrange

    # Act
    dicom_image_redactor_engine = DicomImageRedactorEngine()

    return dicom_image_redactor_engine


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
        "presidio_image_redactor.dicom_image_redactor_engine.copy_files_for_processing",
        return_value=dcm_path,
    )
    mock_convert_dcm_to_png = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.convert_dcm_to_png",
        return_value=[None, None],
    )
    mock_image_open = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.Image.open",
        return_value=None,
    )
    mock_add_padding = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.add_padding",
        return_value=None,
    )
    mock_get_text_metadata = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.get_text_metadata",
        return_value=[None, None, None],
    )
    mock_make_phi_list = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.make_phi_list",
        return_value=None,
    )

    class MockAnalyzer:
        def analyze(self, image: None):
            return None

    mock_create_custom_recognizer = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.create_custom_recognizer",
        return_value=MockAnalyzer(),
    )
    mock_format_bboxes = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.format_bboxes",
        return_value=None,
    )

    class MockInstance:
        def save_as(self, dst_path: str):
            return None

    mock_add_redact_box = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.add_redact_box",
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
    assert mock_create_custom_recognizer.call_count == 1
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
        "presidio_image_redactor.dicom_image_redactor_engine.copy_files_for_processing",
        return_value=dcm_path,
    )
    mock_dcm_files = [
        Path("dir1/dir2/file1.dcm"),
        Path("dir1/dir2/file2.dcm"),
        Path("dir1/dir2/dir3/file3.dcm"),
    ]
    mock_get_all_dcm_files = mocker.patch(
        "presidio_image_redactor.dicom_image_redactor_engine.get_all_dcm_files",
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
# DicomImageRedactorEngine redact()
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
def test_DicomImageRedactorEngine_redact_happy_path(
    mocker,
    mock_engine: DicomImageRedactorEngine,
    dcm_path: str,
    mock_dst_path: Path,
    is_dir: bool,
):
    """Test happy path for DicomImageRedactorEngine redact()

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
        "presidio_image_redactor.dicom_image_redactor_engine.copy_files_for_processing",
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
    mock_engine.redact(dcm_path, "output", 25, "contrast")

    # Assert
    assert mock_validate_paths.call_count == 1
    assert mock_copy_files.call_count == 1
    if is_dir is True:
        assert mock_redact_single.call_count == 0
        assert mock_redact_multiple.call_count == 1
    else:
        assert mock_redact_single.call_count == 1
        assert mock_redact_multiple.call_count == 0
