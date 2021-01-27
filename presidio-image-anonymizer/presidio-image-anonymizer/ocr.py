from PIL import Image
from typing import Union


# TODO implement and test
class OCR:
    """OCR class that performs OCR on a given image."""

    def perform_ocr(self, image: Union[Image, str]) -> dict:
        """Perform OCR on a given image.

        :param image: PIL Image or file path(str) to be processed

        :return: results dictionary containing bboxes and text
        """
        pass
