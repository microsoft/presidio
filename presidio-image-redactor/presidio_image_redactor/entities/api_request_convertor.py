import io
import json
import logging
from typing import Tuple, Union

from PIL import Image

from presidio_image_redactor.entities import InvalidParamException

logger = logging.getLogger("presidio-image-redactor")


def get_json_data(data: str) -> dict:
    """
    Validate incoming json.

    :param data: json with added values for image redaction.
    For now, {"color_fill":"1,1,1"}
    :return: dictionary
    """
    try:
        if not data:
            return {}
        return json.loads(data.replace("'", '"'))
    except Exception as e:
        logger.error(f"failed to parse json from string '{data}' with error {e}")
        raise InvalidParamException(f"Invalid json format '{data}'")


def color_fill_string_to_value(json_params: dict) -> Union[int, Tuple[int, int, int]]:
    """
    Get color_fill and checks it is valid for image redaction.

    color_fill can be an int or Tuple[int, int, int] of (R, G, B)
    :param json_params: {"color_fill":"1,1,1"}
    :return: int or Tuple[int, int, int]
    """
    filling_str = json_params.get("color_fill")
    try:
        if not filling_str:
            return 0, 0, 0
        filling_str_split = filling_str.split(",")
        if len(filling_str_split) == 1:
            return int(filling_str_split[0])
        if len(filling_str_split) != 3:
            raise InvalidParamException(f"Invalid color fill '{filling_str}'")
        return tuple(map(int, filling_str_split))
    except Exception as e:
        logger.error(f"failed to color fill '{filling_str}' with error {e}")
        raise InvalidParamException(f"Invalid color fill '{filling_str}'")


def image_to_byte_array(redacted_image: Image, image_format: str):
    """
    Get an image and return a byte array.

    :param redacted_image: the image which was redacted
    :param image_format: the format of the original image.
    :return:
    """
    img_byte_arr = io.BytesIO()
    redacted_image.save(img_byte_arr, format=image_format)
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr
