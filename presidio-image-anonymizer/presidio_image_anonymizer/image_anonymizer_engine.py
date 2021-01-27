from PIL import Image
from typing import Union, Tuple


# TODO implement and test
class ImageAnonymizerEngine:
    """ImageAnonymizerEngine class only supporting redaction currently."""

    def anonymize(self, image: object, fill: Union[int, Tuple[int, int, int]]) -> Image:
        """Anonymize method to anonymize the given image.

        :param image: PIL Image/numpy array or file path(str) to be processed
        :param fill: colour to fill the shape - int (0-255) for
        grayscale or Tuple(R, G, B) for RGB

        :return: the anonymized image
        """
        pass
