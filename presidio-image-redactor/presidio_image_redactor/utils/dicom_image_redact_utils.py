"""Utils file for de-identifying PHI from DICOM images."""
import copy
import pydicom
from PIL import Image
from typing import Tuple
from pathlib import Path
import tempfile

import presidio_image_redactor
from presidio_image_redactor import ImageAnalyzerEngine
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry, PatternRecognizer

from presidio_image_redactor.utils.dicom_image_utils import (
    check_if_greyscale,
    get_bg_color,
    get_most_common_pixel_value,
    convert_dcm_to_png,
)


def get_text_metadata(instance: pydicom.dataset.FileDataset) -> Tuple[list, list, list]:
    """Retrieve all text metadata from the DICOM image.

    Args:
        instance (pydicom.dataset.FileDataset): Loaded DICOM instance.

    Return:
        metadata_text (list): List of all the instance's element values
            (excluding pixel data).
        is_name (list): True if the element is specified as being a name.
        is_patient (list): True if the element is specified as being
            related to the patient.
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


def process_names(text_metadata: list, is_name: list) -> list:
    """Process names to have multiple iterations in our PHI list.

    Args:
        metadata_text (list): List of all the instance's element values
            (excluding pixel data).
        is_name (list): True if the element is specified as being a name.

    Return:
        phi_list (list): Metadata text with additional name iterations appended.
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


def add_known_generic_phi(phi_list: list) -> list:
    """Add known potential generic PHI values.

    Args:
        phi_list (list): List of PHI to use with Presidio ad-hoc recognizer.

    Return:
        phi_list (list): Same list with added known values.
    """
    phi_list.append("M")
    phi_list.append("[M]")
    phi_list.append("F")
    phi_list.append("[F]")
    phi_list.append("X")
    phi_list.append("[X]")
    phi_list.append("U")
    phi_list.append("[U]")

    return phi_list


def make_phi_list(original_metadata: list, is_name: list, is_patient: list) -> list:
    """Make the list of PHI to use in Presidio ad-hoc recognizer.

    Args:
        original_metadata (list): List of all the instance's element values
            (excluding pixel data).
        is_name (list): True if the element is specified as being a name.
        is_patient (list): True if the element is specified as being
            related to the patient.

    Return:
        phi_str_list (list): List of PHI (str) to use with Presidio ad-hoc recognizer.
    """
    # Process names
    phi_list = process_names(original_metadata, is_name)

    # Add known potential phi values
    phi_list = add_known_generic_phi(phi_list)

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


def create_custom_recognizer(
    phi_list: list,
) -> presidio_image_redactor.image_analyzer_engine.ImageAnalyzerEngine:
    """Create custom recognizer using DICOM metadata.

    Args:
        phi_list (list): List of PHI text pulled from the DICOM metadata.

    Return:
        custom_analyzer_engine (presidio_image_redactor.
            image_analyzer_engine.ImageAnalyzerEngine):
            Custom image analyzer engine.

    """
    # Create recognizer
    deny_list_recognizer = PatternRecognizer(
        supported_entity="PERSON", deny_list=phi_list
    )

    # Add recognizer to registry
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers()
    registry.add_recognizer(deny_list_recognizer)

    # Create analyzer
    analyzer = AnalyzerEngine(registry=registry)
    custom_analyzer_engine = ImageAnalyzerEngine(analyzer_engine=analyzer)

    return custom_analyzer_engine


def get_bboxes_from_analyzer_results(analyzer_results: list) -> dict:
    """Organize bounding box info from analyzer results.

    Args:
        analyzer_results (list): Results from using ImageAnalyzerEngine.

    Return:
        bboxes_dict (dict): Bounding box info organized.
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


def format_bboxes(analyzer_results: list, padding_width: int) -> list:
    """Format the bounding boxes to write directly back to DICOM pixel data.

    Args:
        analyzer_results (list): The analyzer results.
        padding_width (int): Pixel width used for padding (0 if no padding).

    Return:
        bboxes (list): Bounding box information per word.
    """
    if padding_width < 0:
        raise ValueError("Padding width must be a positive number.")

    # Write bounding box info to json files for now
    phi_bboxes_dict = get_bboxes_from_analyzer_results(analyzer_results)

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


def set_bbox_color(instance: pydicom.dataset.FileDataset, box_color_setting: str):
    """Set the bounding box color.

    Args:
        instance (pydicom.dataset.FileDataset): A single DICOM instance.
        box_color_setting (str): Determines how box color is selected.
            'contrast' - Masks stand out relative to background.
            'background' - Masks are same color as background.

    Return:
        box_color (any): int or tuple of int values determining masking box color.
    """
    # Check if we want the box color to contrast with the background
    if box_color_setting.lower() in ["contrast", "invert", "inverted", "inverse"]:
        invert_flag = True
    elif box_color_setting.lower() in ["background", "bg"]:
        invert_flag = False
    else:
        raise ValueError("box_color_setting must be 'contrast' or 'background'")

    # Temporarily save as PNG to get color
    with tempfile.TemporaryDirectory() as tmpdirname:
        dst_path = Path(f"{tmpdirname}/temp.dcm")
        instance.save_as(dst_path)
        _, is_greyscale = convert_dcm_to_png(dst_path, output_dir=tmpdirname)

        png_filepath = f"{tmpdirname}/{dst_path.stem}.png"
        loaded_image = Image.open(png_filepath)
        box_color = get_bg_color(loaded_image, is_greyscale, invert_flag)

    return box_color


def add_redact_box(
    instance: pydicom.dataset.FileDataset,
    bounding_boxes_coordinates: list,
    box_color_setting: str = "contrast",
) -> pydicom.dataset.FileDataset:
    """Add redaction bounding boxes on a DICOM instance.

    Args:
        instance (pydicom.dataset.FileDataset): A single DICOM instance.
        bounding_boxes_coordinates (dict): Bounding box coordinates.
        box_color_setting (str): Determines how box color is selected.
            'contrast' - Masks stand out relative to background.
            'background' - Masks are same color as background.

    Return:
        A new dicom instance with redaction bounding boxes.
    """

    # Copy instance
    redacted_instance = copy.deepcopy(instance)

    # Select masking box color
    is_greyscale = check_if_greyscale(instance)
    if is_greyscale:
        box_color = get_most_common_pixel_value(instance, box_color_setting)
    else:
        box_color = set_bbox_color(redacted_instance, box_color_setting)

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
