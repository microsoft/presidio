import os
import shutil
from copy import deepcopy
import tempfile
from pathlib import Path
from PIL import Image
import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut
import PIL
import png
import numpy as np
from matplotlib import pyplot as plt  # necessary import for PIL typing # noqa: F401
from typing import Tuple, List, Union

from presidio_image_redactor import ImageRedactorEngine
from presidio_image_redactor import ImageAnalyzerEngine  # noqa: F401
from presidio_analyzer import PatternRecognizer


class DicomImageRedactorEngine(ImageRedactorEngine):
    """Performs OCR + PII detection + bounding box redaction.

    :param image_analyzer_engine: Engine which performs OCR + PII detection.
    """

    def redact(
        self,
        image: pydicom.dataset.FileDataset,
        fill: str = "contrast",
        padding_width: int = 25,
        **kwargs,
    ):
        """Redact method to redact the given DICOM image.

        Please note, this method duplicates the image, creates a
        new instance and manipulates it.

        :param image: Loaded DICOM instance including pixel data and metadata.
        :param fill: Fill setting to use for redaction box ("contrast" or "background").
        :param padding_width: Padding width to use when running OCR.
        :param kwargs: Additional values for the analyze method in AnalyzerEngine

        :return: DICOM instance with redacted pixel data.
        """
        instance = deepcopy(image)

        # Load image for processing
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Convert DICOM to PNG and add padding for OCR (during analysis)
            is_greyscale = self._check_if_greyscale(instance)
            image = self._rescale_dcm_pixel_array(instance, is_greyscale)
            self._save_pixel_array_as_png(image, is_greyscale, "tmp_dcm", tmpdirname)

            png_filepath = f"{tmpdirname}/tmp_dcm.png"
            loaded_image = Image.open(png_filepath)
            image = self._add_padding(loaded_image, is_greyscale, padding_width)

        # Create custom recognizer using DICOM metadata
        original_metadata, is_name, is_patient = self._get_text_metadata(instance)
        phi_list = self._make_phi_list(original_metadata, is_name, is_patient)
        deny_list_recognizer = PatternRecognizer(
            supported_entity="PERSON", deny_list=phi_list
        )
        analyzer_results = self.image_analyzer_engine.analyze(
            image, ad_hoc_recognizers=[deny_list_recognizer], **kwargs
        )

        # Redact all bounding boxes from DICOM file
        bboxes = self._format_bboxes(analyzer_results, padding_width)
        redacted_image = self._add_redact_box(instance, bboxes, fill)

        return redacted_image

    def redact_from_file(
        self,
        input_dicom_path: str,
        output_dir: str,
        padding_width: int = 25,
        fill: str = "contrast",
        **kwargs,
    ) -> None:
        """Redact method to redact from a given file.

        Please notice, this method duplicates the file, creates
        new instance and manipulate them.

        :param input_dicom_path: String path to DICOM image.
        :param output_dir: String path to parent output directory.
        :param padding_width : Padding width to use when running OCR.
        :param fill: Color setting to use for redaction box
        ("contrast" or "background").
        :param kwargs: Additional values for the analyze method in AnalyzerEngine
        """
        # Verify the given paths
        if Path(input_dicom_path).is_dir() is True:
            raise TypeError("input_dicom_path must be file (not dir)")
        if Path(input_dicom_path).is_file() is False:
            raise TypeError("input_dicom_path must be a valid file")
        if Path(output_dir).is_file() is True:
            raise TypeError(
                "output_dir must be a directory (does not need to exist yet)"
            )

        # Create duplicate
        dst_path = self._copy_files_for_processing(input_dicom_path, output_dir)

        # Process DICOM file
        output_location = self._redact_single_dicom_image(
            dcm_path=dst_path,
            fill=fill,
            padding_width=padding_width,
            overwrite=True,
            dst_parent_dir=".",
            **kwargs,
        )

        print(f"Output written to {output_location}")

        return None

    def redact_from_directory(
        self,
        input_dicom_path: str,
        output_dir: str,
        padding_width: int = 25,
        fill: str = "contrast",
        **kwargs,
    ) -> None:
        """Redact method to redact from a directory of files.

        Please notice, this method duplicates the files, creates
        new instances and manipulate them.

        :param input_dicom_path: String path to directory of DICOM images.
        :param output_dir: String path to parent output directory.
        :param padding_width : Padding width to use when running OCR.
        :param fill: Color setting to use for redaction box
        ("contrast" or "background").
        :param kwargs: Additional values for the analyze method in AnalyzerEngine
        """
        # Verify the given paths
        if Path(input_dicom_path).is_dir() is False:
            raise TypeError("input_dicom_path must be a valid directory")
        if Path(input_dicom_path).is_file() is True:
            raise TypeError("input_dicom_path must be a directory (not file)")
        if Path(output_dir).is_file() is True:
            raise TypeError(
                "output_dir must be a directory (does not need to exist yet)"
            )

        # Create duplicates
        dst_path = self._copy_files_for_processing(input_dicom_path, output_dir)

        # Process DICOM files
        output_location = self._redact_multiple_dicom_images(
            dcm_dir=dst_path,
            fill=fill,
            padding_width=padding_width,
            overwrite=True,
            dst_parent_dir=".",
            **kwargs,
        )

        print(f"Output written to {output_location}")

        return None

    @staticmethod
    def _get_all_dcm_files(dcm_dir: Path) -> List[Path]:
        """Return paths to all DICOM files in a directory and its sub-directories.

        :param dcm_dir: pathlib Path to a directory containing at least one .dcm file.

        :return: List of pathlib Path objects.
        """
        # Define applicable extensions
        extensions = ["[dD][cC][mM]", "[dD][iI][cC][oO][mM]"]

        # Get all files with any applicable extension
        all_files = []
        for extension in extensions:
            p = dcm_dir.glob(f"**/*.{extension}")
            files = [x for x in p if x.is_file()]
            all_files += files

        return all_files

    @staticmethod
    def _check_if_greyscale(instance: pydicom.dataset.FileDataset) -> bool:
        """Check if a DICOM image is in greyscale.

        :param instance: A single DICOM instance.

        :return: FALSE if the Photometric Interpolation is RGB.
        """
        # Check if image is grayscale or not using the Photometric Interpolation element
        color_scale = instance[0x0028, 0x0004].value
        is_greyscale = color_scale != "RGB"

        return is_greyscale

    @staticmethod
    def _rescale_dcm_pixel_array(
        instance: pydicom.dataset.FileDataset, is_greyscale: bool
    ) -> np.ndarray:
        """Rescale DICOM pixel_array.

        :param instance: A singe DICOM instance.
        :param is_greyscale: FALSE if the Photometric Interpolation is RGB.

        :return: Rescaled DICOM pixel_array.
        """
        # Normalize contrast
        if "WindowWidth" in instance:
            image_2d = apply_voi_lut(instance.pixel_array, instance)
        else:
            image_2d = instance.pixel_array

        # Convert to float to avoid overflow or underflow losses.
        image_2d_float = image_2d.astype(float)

        if not is_greyscale:
            image_2d_scaled = image_2d_float
        else:
            # Rescaling grey scale between 0-255
            image_2d_scaled = (
                np.maximum(image_2d_float, 0) / image_2d_float.max()
            ) * 255.0

        # Convert to uint
        image_2d_scaled = np.uint8(image_2d_scaled)

        return image_2d_scaled

    @staticmethod
    def _save_pixel_array_as_png(
        pixel_array: np.array,
        is_greyscale: bool,
        output_file_name: str = "example",
        output_dir: str = "temp_dir",
    ) -> None:
        """Save the pixel data from a loaded DICOM instance as PNG.

        :param pixel_array: Pixel data from the instance.
        :param is_greyscale: True if image is greyscale.
        :param output_file_name: Name of output file (no file extension).
        :param output_dir: String path to output directory.
        """
        shape = pixel_array.shape

        # Write the PNG file
        os.makedirs(output_dir, exist_ok=True)
        if is_greyscale:
            with open(f"{output_dir}/{output_file_name}.png", "wb") as png_file:
                w = png.Writer(shape[1], shape[0], greyscale=True)
                w.write(png_file, pixel_array)
        else:
            with open(f"{output_dir}/{output_file_name}.png", "wb") as png_file:
                w = png.Writer(shape[1], shape[0], greyscale=False)
                # Semi-flatten the pixel array to RGB representation in 2D
                pixel_array = np.reshape(pixel_array, (shape[0], shape[1] * 3))
                w.write(png_file, pixel_array)

        return None

    @classmethod
    def _convert_dcm_to_png(cls, filepath: Path, output_dir: str = "temp_dir") -> tuple:
        """Convert DICOM image to PNG file.

        :param filepath: pathlib Path to a single dcm file.
        :param output_dir: String path to output directory.

        :return: Shape of pixel array and if image mode is greyscale.
        """
        ds = pydicom.dcmread(filepath)

        # Check if image is grayscale using the Photometric Interpolation element
        is_greyscale = cls._check_if_greyscale(ds)

        # Rescale pixel array
        image = cls._rescale_dcm_pixel_array(ds, is_greyscale)
        shape = image.shape

        # Write to PNG file
        cls._save_pixel_array_as_png(image, is_greyscale, filepath.stem, output_dir)

        return shape, is_greyscale

    @staticmethod
    def _get_bg_color(
        image: PIL.PngImagePlugin.PngImageFile, is_greyscale: bool, invert: bool = False
    ) -> Union[int, Tuple[int, int, int]]:
        """Select most common color as background color.

        :param image: Loaded PNG image.
        :param colorscale: Colorscale of image (e.g., 'grayscale', 'RGB')
        :param invert: TRUE if you want to get the inverse of the bg color.

        :return: Background color.
        """
        # Invert colors if invert flag is True
        if invert:
            if image.mode == "RGBA":
                # Handle transparency as needed
                r, g, b, a = image.split()
                rgb_image = Image.merge("RGB", (r, g, b))
                inverted_image = PIL.ImageOps.invert(rgb_image)
                r2, g2, b2 = inverted_image.split()

                image = Image.merge("RGBA", (r2, g2, b2, a))

            else:
                image = PIL.ImageOps.invert(image)

        # Get background color
        if is_greyscale:
            # Select most common color as color
            bg_color = int(np.bincount(list(image.getdata())).argmax())
        else:
            # Reduce size of image to 1 pixel to get dominant color
            tmp_image = image.copy()
            tmp_image = tmp_image.resize((1, 1), resample=0)
            bg_color = tmp_image.getpixel((0, 0))

        return bg_color

    @classmethod
    def _get_most_common_pixel_value(
        cls, instance: pydicom.dataset.FileDataset, fill: str = "contrast"
    ) -> Union[int, Tuple[int, int, int]]:
        """Find the most common pixel value.

        :param instance: A singe DICOM instance.
        :param fill: Determines how box color is selected.
        'contrast' - Masks stand out relative to background.
        'background' - Masks are same color as background.

        :return: Most or least common pixel value (depending on fill).
        """
        # Get flattened pixel array
        flat_pixel_array = np.array(instance.pixel_array).flatten()

        is_greyscale = cls._check_if_greyscale(instance)
        if is_greyscale:
            # Get most common value
            values, counts = np.unique(flat_pixel_array, return_counts=True)
            flat_pixel_array = np.array(flat_pixel_array)
            common_value = values[np.argmax(counts)]
        else:
            raise TypeError(
                "Most common pixel value retrieval is only supported for greyscale images at this point."  # noqa: E501
            )

        # Invert color as necessary
        if fill.lower() in ["contrast", "invert", "inverted", "inverse"]:
            pixel_value = np.max(flat_pixel_array) - common_value
        elif fill.lower() in ["background", "bg"]:
            pixel_value = common_value

        return pixel_value

    @classmethod
    def _add_padding(
        cls,
        image: PIL.PngImagePlugin.PngImageFile,
        is_greyscale: bool,
        padding_width: int,
    ) -> PIL.PngImagePlugin.PngImageFile:
        """Add border to image using most common color.

        :param image: Loaded PNG image.
        :param is_greyscale: Whether image is in grayscale or not.
        :param padding_width: Pixel width of padding (uniform).

        :return: PNG image with padding.
        """
        # Check padding width value
        if padding_width <= 0:
            raise ValueError("Enter a positive value for padding")
        elif padding_width >= 100:
            raise ValueError(
                "Excessive padding width entered. Please use a width under 100 pixels."  # noqa: E501
            )

        # Select most common color as border color
        border_color = cls._get_bg_color(image, is_greyscale)

        # Add padding
        right = padding_width
        left = padding_width
        top = padding_width
        bottom = padding_width

        width, height = image.size

        new_width = width + right + left
        new_height = height + top + bottom

        image_with_padding = Image.new(
            image.mode, (new_width, new_height), border_color
        )
        image_with_padding.paste(image, (left, top))

        return image_with_padding

    @staticmethod
    def _copy_files_for_processing(src_path: str, dst_parent_dir: str) -> Path:
        """Copy DICOM files. All processing should be done on the copies.

        :param src_path: String path to DICOM file or directory containing DICOM files.
        :param dst_parent_dir: String path to parent directory of output location.

        :return: Output location of the file(s).
        """
        # Identify output path
        tail = list(Path(src_path).parts)[-1]
        dst_path = Path(dst_parent_dir, tail)

        # Copy file(s)
        if Path(src_path).is_dir() is True:
            try:
                shutil.copytree(src_path, dst_path)
            except FileExistsError:
                raise FileExistsError(
                    "Destination files already exist. Please clear the destination files or specify a different dst_parent_dir."  # noqa: E501
                )
        elif Path(src_path).is_file() is True:
            # Create the output dir manually if working with a single file
            os.makedirs(Path(dst_path).parent, exist_ok=True)
            shutil.copy(src_path, dst_path)
        else:
            raise FileNotFoundError(f"{src_path} does not exist")

        return dst_path

    @staticmethod
    def _get_text_metadata(
        instance: pydicom.dataset.FileDataset,
    ) -> Tuple[list, list, list]:
        """Retrieve all text metadata from the DICOM image.

        :param instance: Loaded DICOM instance.

        :return: List of all the instance's element values (excluding pixel data),
        bool for if the element is specified as being a name,
        bool for if the element is specified as being related to the patient.
        """
        metadata_text = list()
        is_name = list()
        is_patient = list()

        for element in instance:
            # Save all metadata except the DICOM image itself
            if element.name != "Pixel Data":
                # Save the metadata
                metadata_text.append(element.value)

                # Track whether this particular element is a name
                if "name" in element.name.lower():
                    is_name.append(True)
                else:
                    is_name.append(False)

                # Track whether this particular element is directly tied to the patient
                if "patient" in element.name.lower():
                    is_patient.append(True)
                else:
                    is_patient.append(False)
            else:
                metadata_text.append("")
                is_name.append(False)
                is_patient.append(False)

        return metadata_text, is_name, is_patient

    @staticmethod
    def _process_names(text_metadata: list, is_name: list) -> list:
        """Process names to have multiple iterations in our PHI list.

        :param metadata_text: List of all the instance's element values
        (excluding pixel data).
        :param is_name: True if the element is specified as being a name.

        :return: Metadata text with additional name iterations appended.
        """
        phi_list = text_metadata.copy()

        for i in range(0, len(text_metadata)):
            if is_name[i] is True:
                original_text = str(text_metadata[i])

                # Replacing separator character with space
                text_1 = original_text.replace("^", " ")

                # Capitalize all characters in name
                text_2 = text_1.upper()

                # Lowercase all characters in name
                text_3 = text_1.lower()

                # Capitalize first letter in each name
                text_4 = text_1.title()

                # Append iterations
                phi_list.append(text_1)
                phi_list.append(text_2)
                phi_list.append(text_3)
                phi_list.append(text_4)

                # Adding each name as a separate item in the list
                phi_list = phi_list + text_1.split(" ")
                phi_list = phi_list + text_2.split(" ")
                phi_list = phi_list + text_3.split(" ")
                phi_list = phi_list + text_4.split(" ")

        return phi_list

    @staticmethod
    def _add_known_generic_phi(phi_list: list) -> list:
        """Add known potential generic PHI values.

        :param phi_list: List of PHI to use with Presidio ad-hoc recognizer.

        :return: Same list with added known values.
        """
        known_generic_phi = ["[M]", "[F]", "[X]", "[U]", "M", "F", "X", "U"]
        phi_list.extend(known_generic_phi)

        return phi_list

    @classmethod
    def _make_phi_list(
        cls,
        original_metadata: List[Union[pydicom.multival.MultiValue, list, tuple]],
        is_name: List[bool],
        is_patient: List[bool],
    ) -> list:
        """Make the list of PHI to use in Presidio ad-hoc recognizer.

        :param original_metadata: List of all the instance's element values
        (excluding pixel data).
        :param is_name: True if the element is specified as being a name.
        :param is_patient: True if the element is specified as being
        related to the patient.

        :return: List of PHI (str) to use with Presidio ad-hoc recognizer.
        """
        # Process names
        phi_list = cls._process_names(original_metadata, is_name)

        # Add known potential phi values
        phi_list = cls._add_known_generic_phi(phi_list)

        # Flatten any nested lists
        for phi in phi_list:
            if type(phi) in [pydicom.multival.MultiValue, list, tuple]:
                for item in phi:
                    phi_list.append(item)
                phi_list.remove(phi)

        # Convert all items to strings
        phi_str_list = [str(phi) for phi in phi_list]

        # Remove duplicates
        phi_str_list = list(set(phi_str_list))

        return phi_str_list

    @staticmethod
    def _get_bboxes_from_analyzer_results(analyzer_results: list) -> dict:
        """Organize bounding box info from analyzer results.

        :param analyzer_results: Results from using ImageAnalyzerEngine.

        :return: Bounding box info organized.
        """
        bboxes_dict = {}
        for i in range(0, len(analyzer_results)):
            result = analyzer_results[i].to_dict()

            bboxes_dict[str(i)] = {
                "entity_type": result["entity_type"],
                "score": result["score"],
                "left": result["left"],
                "top": result["top"],
                "width": result["width"],
                "height": result["height"],
            }

        return bboxes_dict

    @classmethod
    def _format_bboxes(cls, analyzer_results: list, padding_width: int) -> List[dict]:
        """Format the bounding boxes to write directly back to DICOM pixel data.

        :param analyzer_results: The analyzer results.
        :param padding_width: Pixel width used for padding (0 if no padding).

        :return: Bounding box information per word.
        """
        if padding_width < 0:
            raise ValueError("Padding width must be a positive number.")

        # Write bounding box info to json files for now
        phi_bboxes_dict = cls._get_bboxes_from_analyzer_results(analyzer_results)

        # convert detected bounding boxes to list
        bboxes = [phi_bboxes_dict[i] for i in phi_bboxes_dict.keys()]

        # remove padding from all bounding boxes
        bboxes = [
            {
                "top": max(0, bbox["top"] - padding_width),
                "left": max(0, bbox["left"] - padding_width),
                "width": bbox["width"],
                "height": bbox["height"],
            }
            for bbox in bboxes
        ]

        return bboxes

    @classmethod
    def _set_bbox_color(
        cls, instance: pydicom.dataset.FileDataset, fill: str
    ) -> Union[int, Tuple[int, int, int]]:
        """Set the bounding box color.

        :param instance: A single DICOM instance.
        :param fill: Determines how box color is selected.
        'contrast' - Masks stand out relative to background.
        'background' - Masks are same color as background.

        :return: int or tuple of int values determining masking box color.
        """
        # Check if we want the box color to contrast with the background
        if fill.lower() in ["contrast", "invert", "inverted", "inverse"]:
            invert_flag = True
        elif fill.lower() in ["background", "bg"]:
            invert_flag = False
        else:
            raise ValueError("fill must be 'contrast' or 'background'")

        # Temporarily save as PNG to get color
        with tempfile.TemporaryDirectory() as tmpdirname:
            dst_path = Path(f"{tmpdirname}/temp.dcm")
            instance.save_as(dst_path)
            _, is_greyscale = cls._convert_dcm_to_png(dst_path, output_dir=tmpdirname)

            png_filepath = f"{tmpdirname}/{dst_path.stem}.png"
            loaded_image = Image.open(png_filepath)
            box_color = cls._get_bg_color(loaded_image, is_greyscale, invert_flag)

        return box_color

    @classmethod
    def _add_redact_box(
        cls,
        instance: pydicom.dataset.FileDataset,
        bounding_boxes_coordinates: list,
        fill: str = "contrast",
    ) -> pydicom.dataset.FileDataset:
        """Add redaction bounding boxes on a DICOM instance.

        :param instance: A single DICOM instance.
        :param bounding_boxes_coordinates: Bounding box coordinates.
        :param fill: Determines how box color is selected.
        'contrast' - Masks stand out relative to background.
        'background' - Masks are same color as background.

        :return: A new dicom instance with redaction bounding boxes.
        """
        # Copy instance
        redacted_instance = deepcopy(instance)

        # Select masking box color
        is_greyscale = cls._check_if_greyscale(instance)
        if is_greyscale:
            box_color = cls._get_most_common_pixel_value(instance, fill)
        else:
            box_color = cls._set_bbox_color(redacted_instance, fill)

        # Apply mask
        for i in range(0, len(bounding_boxes_coordinates)):
            bbox = bounding_boxes_coordinates[i]
            top = bbox["top"]
            left = bbox["left"]
            width = bbox["width"]
            height = bbox["height"]
            redacted_instance.pixel_array[
                top : top + height, left : left + width
            ] = box_color

        redacted_instance.PixelData = redacted_instance.pixel_array.tobytes()

        return redacted_instance

    def _redact_single_dicom_image(
        self,
        dcm_path: str,
        fill: str,
        padding_width: int,
        overwrite: bool,
        dst_parent_dir: str,
        **kwargs,
    ) -> str:
        """Redact text PHI present on a DICOM image.

        :param dcm_path: String path to the DICOM file.
        :param fill: Color setting to use for bounding boxes
        ("contrast" or "background").
        :param padding_width: Pixel width of padding (uniform).
        :param overwrite: Only set to True if you are providing the
        duplicated DICOM path in dcm_path.
        :param dst_parent_dir: String path to parent directory of where to store copies.
        :param kwargs: Additional values for the analyze method in AnalyzerEngine

        :return: Path to the output DICOM file.
        """
        # Ensure we are working on a single file
        if Path(dcm_path).is_dir():
            raise FileNotFoundError("Please ensure dcm_path is a single file")
        elif Path(dcm_path).is_file() is False:
            raise FileNotFoundError(f"{dcm_path} does not exist")

        # Copy file before processing if overwrite==False
        if overwrite is False:
            dst_path = self._copy_files_for_processing(dcm_path, dst_parent_dir)
        else:
            dst_path = dcm_path

        # Load instance
        instance = pydicom.dcmread(dst_path)

        # Load image for processing
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Convert DICOM to PNG and add padding for OCR (during analysis)
            _, is_greyscale = self._convert_dcm_to_png(dst_path, output_dir=tmpdirname)
            png_filepath = f"{tmpdirname}/{dst_path.stem}.png"
            loaded_image = Image.open(png_filepath)
            image = self._add_padding(loaded_image, is_greyscale, padding_width)

        # Create custom recognizer using DICOM metadata
        original_metadata, is_name, is_patient = self._get_text_metadata(instance)
        phi_list = self._make_phi_list(original_metadata, is_name, is_patient)
        deny_list_recognizer = PatternRecognizer(
            supported_entity="PERSON", deny_list=phi_list
        )
        analyzer_results = self.image_analyzer_engine.analyze(
            image, ad_hoc_recognizers=[deny_list_recognizer], **kwargs
        )

        # Redact all bounding boxes from DICOM file
        bboxes = self._format_bboxes(analyzer_results, padding_width)
        redacted_dicom_instance = self._add_redact_box(instance, bboxes, fill)
        redacted_dicom_instance.save_as(dst_path)

        return dst_path

    def _redact_multiple_dicom_images(
        self,
        dcm_dir: str,
        fill: str,
        padding_width: int,
        overwrite: bool,
        dst_parent_dir: str,
        **kwargs,
    ) -> str:
        """Redact text PHI present on all DICOM images in a directory.

        :param dcm_dir: String path to directory containing DICOM files (can be nested).
        :param fill: Color setting to use for bounding boxes
        ("contrast" or "background").
        :param padding_width: Pixel width of padding (uniform).
        :param overwrite: Only set to True if you are providing
        the duplicated DICOM dir in dcm_dir.
        :param dst_parent_dir: String path to parent directory of where to store copies.
        :param kwargs: Additional values for the analyze method in AnalyzerEngine

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
            dst_dir = self._copy_files_for_processing(dcm_dir, dst_parent_dir)
        else:
            dst_dir = dcm_dir

        # Process each DICOM file directly
        all_dcm_files = self._get_all_dcm_files(Path(dst_dir))
        for dst_path in all_dcm_files:
            self._redact_single_dicom_image(
                dst_path, fill, padding_width, overwrite, dst_parent_dir, **kwargs
            )

        return dst_dir
