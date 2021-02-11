import json
import logging
from typing import Tuple, Union, io

from PIL import Image

from presidio_image_anonymizer.entities import InvalidParamException

logger = logging.getLogger("presidio-image-anonymizer")


def get_json_data(data: str) -> dict:
    try:
        if not data:
            return {}
        return json.loads(data.replace("'", "\""))
    except Exception as e:
        logger.error(
            f"failed to parse json from string '{data}' with error {e}")
        raise InvalidParamException(f"Invalid json format \'{data}\'")


def color_fill_string_to_value(json_params: dict) -> Union[int, Tuple[int, int, int]]:
    filling_str = json_params.get("color_fill")
    try:
        if not filling_str:
            return 0, 0, 0
        filling_str_split = filling_str.split(',')
        if len(filling_str_split) == 1:
            return int(filling_str_split[0])
        if len(filling_str_split) != 3:
            raise InvalidParamException(f"Invalid color fill \'{filling_str}\'")
        return tuple(map(int, filling_str_split))
    except Exception as e:
        logger.error(
            f"failed to color fill '{filling_str}' with error {e}")
        raise InvalidParamException(f"Invalid color fill \'{filling_str}\'")


def image_to_byte_array(anonymized_image: Image, image_format: str):
    img_byte_arr = io.BytesIO()
    anonymized_image.save(img_byte_arr,
                          format=image_format)
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr
