"""Utils file for DICOM image operations."""
import os
from pathlib import Path
import shutil

import pydicom
from pydicom.pixel_data_handlers.util import apply_voi_lut
import numpy as np
import PIL
from PIL import Image
import png
from matplotlib import pyplot as plt  # necessary import for PIL typing # noqa: F401
from typing import List, Union, Tuple


def get_all_dcm_files(dcm_dir: Path) -> List[Path]:
    """Return paths to all DICOM files in a directory and its sub-directories.

    Args:
        dcm_dir (pathlib.Path): Path to a directory containing at least one .dcm file.

    Return:
        files (list): List of pathlib Path objects.
    """
    # Define applicable extensions (case-insensitive)
    extensions = ["dcm", "dicom"]

    # Get all files with any applicable extension
    all_files = []
    for extension in extensions:
        p = dcm_dir.glob(f"**/*.{extension}")
        files = [x for x in p if x.is_file()]
        all_files += files

    return all_files


def check_if_greyscale(instance: pydicom.dataset.FileDataset) -> bool:
    """Check if a DICOM image is in greyscale.

    Args:
        instance (pydicom.dataset.FileDataset): A single DICOM instance.

    Return:
        is_greyscale (bool): FALSE if the Photometric Interpolation is RGB.
    """
    # Check if image is grayscale or not using the Photometric Interpolation element
    color_scale = instance[0x0028, 0x0004].value
    is_greyscale = color_scale != "RGB"  # TODO: Make this more robust

    return is_greyscale


def rescale_dcm_pixel_array(
    instance: pydicom.dataset.FileDataset, is_greyscale: bool
) -> np.ndarray:
    """Rescale DICOM pixel_array.

    Args:
        instance (pydicom.dataset.FileDataset): a singe DICOM instance.
        is_greyscale (bool): FALSE if the Photometric Interpolation is RGB.

    Return:
        image_2d_scaled (numpy.ndarray): rescaled DICOM pixel_array.
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
        image_2d_scaled = (np.maximum(image_2d_float, 0) / image_2d_float.max()) * 255.0

    # Convert to uint
    image_2d_scaled = np.uint8(image_2d_scaled)

    return image_2d_scaled


def convert_dcm_to_png(filepath: Path, output_dir: str = "temp_dir") -> tuple:
    """Convert DICOM image to PNG file.

    Args:
        filepath (pathlib.Path): Path to a single dcm file.
        output_dir (str): Path to output directory.

    Return:
        shape (tuple): Returns shape of pixel array.
        is_greyscale (bool): FALSE if the Photometric Interpolation is RGB.
    """
    ds = pydicom.dcmread(filepath)

    # Check if image is grayscale or not using the Photometric Interpolation element
    is_greyscale = check_if_greyscale(ds)

    image = rescale_dcm_pixel_array(ds, is_greyscale)
    shape = image.shape

    # Write the PNG file
    os.makedirs(output_dir, exist_ok=True)
    if is_greyscale:
        with open(f"{output_dir}/{filepath.stem}.png", "wb") as png_file:
            w = png.Writer(shape[1], shape[0], greyscale=True)
            w.write(png_file, image)
    else:
        with open(f"{output_dir}/{filepath.stem}.png", "wb") as png_file:
            w = png.Writer(shape[1], shape[0], greyscale=False)
            # Semi-flatten the pixel array to get RGB representation in two dimensions
            pixel_array = np.reshape(ds.pixel_array, (shape[0], shape[1] * 3))
            w.write(png_file, pixel_array)

    return shape, is_greyscale


def get_bg_color(
    image: PIL.PngImagePlugin.PngImageFile, is_greyscale: bool, invert: bool = False
) -> Union[int, Tuple[int, int, int]]:
    """Select most common color as background color.

    Args:
        image (PIL.PngImagePlugin.PngImageFile): Loaded PNG image.
        colorscale (str): Colorscale of image (e.g., 'grayscale', 'RGB')
        invert (bool): TRUE if you want to get the inverse of the bg color.

    Return:
        bg_color (tuple): Background color.
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


def get_most_common_pixel_value(
    instance: pydicom.dataset.FileDataset, box_color_setting: str = "contrast"
) -> Union[int, Tuple[int, int, int]]:
    """Find the most common pixel value.

    Args:
        instance (pydicom.dataset.FileDataset): a singe DICOM instance.
        box_color_setting (str): Determines how box color is selected.
            'contrast' - Masks stand out relative to background.
            'background' - Masks are same color as background.

    Return:
        pixel_value (int or tuple of int): Most or least common pixel value
            (depending on box_color_setting).
    """
    # Get flattened pixel array
    flat_pixel_array = np.array(instance.pixel_array).flatten()

    is_greyscale = check_if_greyscale(instance)
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
    if box_color_setting.lower() in ["contrast", "invert", "inverted", "inverse"]:
        pixel_value = np.max(flat_pixel_array) - common_value
    elif box_color_setting.lower() in ["background", "bg"]:
        pixel_value = common_value

    return pixel_value


def add_padding(
    image: PIL.PngImagePlugin.PngImageFile, is_greyscale: bool, padding_width: int
) -> PIL.PngImagePlugin.PngImageFile:
    """Add border to image using most common color.

    Args:
        image (PIL.PngImagePlugin.PngImageFile): Loaded PNG image.
        is_greyscale (bool): Whether image is in grayscale or not.
        padding_width (int): Pixel width of padding (uniform).

    Return:
        image_with_padding (PIL.PngImagePlugin.PngImageFile): PNG image with padding.
    """
    # Check padding width value
    if padding_width <= 0:
        raise ValueError("Enter a positive value for padding")
    elif padding_width >= 100:
        raise ValueError(
            "Excessive padding width entered. Please use a width under 100 pixels."
        )

    # Select most common color as border color
    border_color = get_bg_color(image, is_greyscale)

    # Add padding
    right = padding_width
    left = padding_width
    top = padding_width
    bottom = padding_width

    width, height = image.size

    new_width = width + right + left
    new_height = height + top + bottom

    image_with_padding = Image.new(image.mode, (new_width, new_height), border_color)
    image_with_padding.paste(image, (left, top))

    return image_with_padding


def copy_files_for_processing(src_path: str, dst_parent_dir: str) -> Path:
    """Copy DICOM files. All processing should be done on the copies.

    Args:
        src_path (str): Source DICOM file or directory containing DICOM files.
        dst_parent_dir (str): Parent directory of where you want to store the copies.

    Return:
        dst_path (pathlib.Path): Output location of the file(s).
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
