import math
import operator
import os
from functools import reduce

from PIL import Image


def compare_images(image_one: Image, image_two: Image):
    i1 = image_one.histogram()
    i2 = image_two.histogram()

    result = math.sqrt(
        reduce(operator.add, map(lambda a, b: (a - b) ** 2, i1, i2)) / len(i1)
    )
    return result == 0


def get_resource_image(file_name: str) -> Image:
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, "resources", file_name)
    return Image.open(file_path)
