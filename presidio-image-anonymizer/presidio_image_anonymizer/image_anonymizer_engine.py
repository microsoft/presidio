from PIL import Image, ImageDraw
from typing import Union, Tuple
from presidio_image_anonymizer.image_analyzer_engine import ImageAnalyzerEngine


# TODO implement and test
class ImageAnonymizerEngine:
    """ImageAnonymizerEngine class only supporting redaction currently."""

    def anonymize(
        self, image: object, fill: Union[int, Tuple[int, int, int]] = (0, 0, 0)
    ) -> Image:
        """Anonymize method to anonymize the given image.

        :param image: PIL Image/numpy array or file path(str) to be processed
        :param fill: colour to fill the shape - int (0-255) for
        grayscale or Tuple(R, G, B) for RGB

        :return: the anonymized image
        """
        bboxes = ImageAnalyzerEngine().analyze(image)

        im = Image.open(image)
        draw = ImageDraw.Draw(im)

        for box in bboxes:
            x0 = box.left
            y0 = box.top
            x1 = x0 + box.width
            y1 = y0 + box.height
            draw.rectangle([x0, y0, x1, y1], fill=fill)

        return im
