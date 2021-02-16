from typing import Union, Tuple

from PIL import Image, ImageDraw, ImageChops

from presidio_image_redactor.image_analyzer_engine import ImageAnalyzerEngine


class ImageRedactorEngine:
    """ImageRedactorEngine class only supporting redaction currently."""

    def __init__(self):
        self.analyzer_engine = ImageAnalyzerEngine()

    def redact(
        self, image: Image, fill: Union[int, Tuple[int, int, int]] = (0, 0, 0)
    ) -> Image:
        """Redact method to redact the given image.

        Please notice, this method duplicates the image, creates a new instance and
        manipulate it.
        :param image: PIL Image to be processed
        :param fill: colour to fill the shape - int (0-255) for
        grayscale or Tuple(R, G, B) for RGB

        :return: the redacted image
        """

        image = ImageChops.duplicate(image)

        bboxes = self.analyzer_engine.analyze(image)
        draw = ImageDraw.Draw(image)

        for box in bboxes:
            x0 = box.left
            y0 = box.top
            x1 = x0 + box.width
            y1 = y0 + box.height
            draw.rectangle([x0, y0, x1, y1], fill=fill)

        return image
