from PIL import Image
from pathlib import Path
import tempfile
import pydicom

from presidio_image_redactor.utils.dicom_image_utils import (
    copy_files_for_processing,
    get_all_dcm_files,
    convert_dcm_to_png,
    add_padding,
)
from presidio_image_redactor.utils.dicom_image_redact_utils import (
    get_text_metadata,
    make_phi_list,
    create_custom_recognizer,
    format_bboxes,
    add_redact_box,
)


class DicomImageRedactorEngine:
    """Performs OCR + PII detection + bounding box redaction.

    :param image_analyzer_engine: Engine which performs OCR + PII detection.
    """

    def _validate_paths(self, input_path: str, output_dir: str) -> None:
        """Validate the DICOM path.

        Args:
            input_path (str): Path to input DICOM file or dir.
            output_dir (str): Path to parent directory to write output to.
        """
        # Check input is an actual file or dir
        if Path(input_path).is_dir() is False:
            if Path(input_path).is_file() is False:
                raise TypeError("input_path must be valid file or dir")

        # Check output is a directory
        if Path(output_dir).is_file() is True:
            raise TypeError(
                "output_dir must be a directory (does not need to exist yet)"
            )

    def _redact_single_dicom_image(
        self,
        dcm_path: str,
        box_color_setting: str,
        padding_width: int,
        overwrite: bool,
        dst_parent_dir: str,
    ) -> str:
        """Redact text PHI present on a DICOM image.

        Args:
            dcm_path (pathlib.Path): Path to the DICOM file.
            box_color_setting (str): Color setting to use for bounding boxes
                ("contrast" or "background").
            padding_width (int): Pixel width of padding (uniform).
            overwrite (bool): Only set to True if you are providing the
                duplicated DICOM path in dcm_path.
            dst_parent_dir (str): Parent directory of where you want to
                store the copies.

        Return:
            dst_path (str): Path to the output DICOM file.
        """
        # Ensure we are working on a single file
        if Path(dcm_path).is_dir():
            raise FileNotFoundError("Please ensure dcm_path is a single file")
        elif Path(dcm_path).is_file() is False:
            raise FileNotFoundError(f"{dcm_path} does not exist")

        # Copy file before processing if overwrite==False
        if overwrite is False:
            dst_path = copy_files_for_processing(dcm_path, dst_parent_dir)
        else:
            dst_path = dcm_path

        # Load instance
        instance = pydicom.dcmread(dst_path)

        # Load image for processing
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Convert DICOM to PNG and add padding for OCR (during analysis)
            _, is_greyscale = convert_dcm_to_png(dst_path, output_dir=tmpdirname)
            png_filepath = f"{tmpdirname}/{dst_path.stem}.png"
            loaded_image = Image.open(png_filepath)
            image = add_padding(loaded_image, is_greyscale, padding_width)

        # Create custom recognizer using DICOM metadata
        original_metadata, is_name, is_patient = get_text_metadata(instance)
        phi_list = make_phi_list(original_metadata, is_name, is_patient)
        custom_analyzer_engine = create_custom_recognizer(phi_list)
        analyzer_results = custom_analyzer_engine.analyze(image)

        # Redact all bounding boxes from DICOM file
        bboxes = format_bboxes(analyzer_results, padding_width)
        redacted_dicom_instance = add_redact_box(instance, bboxes, box_color_setting)
        redacted_dicom_instance.save_as(dst_path)

        return dst_path

    def _redact_multiple_dicom_images(
        self,
        dcm_dir: str,
        box_color_setting: str,
        padding_width: int,
        overwrite: bool,
        dst_parent_dir: str,
    ) -> str:
        """Redact text PHI present on all DICOM images in a directory.

        Args:
            dcm_dir (str): Directory containing DICOM files (can be nested).
            box_color_setting (str): Color setting to use for bounding boxes
                ("contrast" or "background").
            padding_width (int): Pixel width of padding (uniform).
            overwrite (bool): Only set to True if you are providing
                the duplicated DICOM dir in dcm_dir.
            dst_parent_dir (str): Parent directory of where you want to
                store the copies.

        Return:
            dst_dir (str): Path to the output DICOM directory.
        """
        # Ensure we are working on a directory (can have sub-directories)
        if Path(dcm_dir).is_file():
            raise FileNotFoundError("Please ensure dcm_path is a directory")
        elif Path(dcm_dir).is_dir() is False:
            raise FileNotFoundError(f"{dcm_dir} does not exist")

        # List of files to process directly
        if overwrite is False:
            dst_dir = copy_files_for_processing(dcm_dir, dst_parent_dir)
        else:
            dst_dir = dcm_dir

        # Process each DICOM file directly
        all_dcm_files = get_all_dcm_files(Path(dst_dir))
        for dst_path in all_dcm_files:
            self._redact_single_dicom_image(
                dst_path, box_color_setting, padding_width, overwrite, dst_parent_dir
            )

        return dst_dir

    def redact(
        self,
        input_dicom_path: str,
        output_dir: str,
        padding_width: int = 25,
        box_color_setting: str = "contrast",
    ) -> None:
        """Redact method to redact the given image.

        Please notice, this method duplicates the image, creates a
        new instance and manipulate it.

        Args:
            input_dicom_path (str): Path to DICOM image(s).
            output_dir (str): Parent output directory.
            padding_width (int): Padding width to use when running OCR.
            box_color_setting (str): Color setting to use for redaction box
                ("contrast" or "background").
        """
        # Verify the given paths
        self._validate_paths(input_dicom_path, output_dir)

        # Create duplicate(s)
        dst_path = copy_files_for_processing(input_dicom_path, output_dir)

        # Process DICOM file(s)
        if Path(dst_path).is_dir() is False:
            output_location = self._redact_single_dicom_image(
                dcm_path=dst_path,
                box_color_setting=box_color_setting,
                padding_width=padding_width,
                overwrite=True,
                dst_parent_dir=".",
            )
        else:
            output_location = self._redact_multiple_dicom_images(
                dcm_dir=dst_path,
                box_color_setting=box_color_setting,
                padding_width=padding_width,
                overwrite=True,
                dst_parent_dir=".",
            )

        print(f"Output location: {output_location}")

        return None
