from typing import Union, Tuple, Optional

from PIL import Image, ImageDraw, ImageChops

from presidio_image_redactor import ImageAnalyzerEngine, BboxProcessor


class ImageRedactorEngine:
    """ImageRedactorEngine performs OCR + PII detection + bounding box redaction.

    :param image_analyzer_engine: Engine which performs OCR + PII detection.
    """

    def __init__(self, image_analyzer_engine: ImageAnalyzerEngine = None):
        if not image_analyzer_engine:
            self.image_analyzer_engine = ImageAnalyzerEngine()
        else:
            self.image_analyzer_engine = image_analyzer_engine

        self.bbox_processor = BboxProcessor()

    def redact(
        self,
        image: Image,
        fill: Union[int, Tuple[int, int, int]] = (0, 0, 0),
        ocr_kwargs: Optional[dict] = None,
        **text_analyzer_kwargs,
    ) -> Image:
        """Redact method to redact the given image.

        Please notice, this method duplicates the image, creates a new instance and
        manipulate it.
        :param image: PIL Image to be processed.
        :param fill: colour to fill the shape - int (0-255) for
        grayscale or Tuple(R, G, B) for RGB.
        :param ocr_kwargs: Additional params for OCR methods.
        :param text_analyzer_kwargs: Additional values for the analyze method
        in AnalyzerEngine.

        :return: the redacted image
        """

        image = ImageChops.duplicate(image)

        bboxes = self.image_analyzer_engine.analyze(
            image, ocr_kwargs, **text_analyzer_kwargs
        )
        draw = ImageDraw.Draw(image)

        for box in bboxes:
            x0 = box.left
            y0 = box.top
            x1 = x0 + box.width
            y1 = y0 + box.height
            draw.rectangle([x0, y0, x1, y1], fill=fill)

        return image
