from typing import List
from presidio_image_anonymizer.image_recognizer_result import ImageRecognizerResult
from presidio_analyzer import RecognizerResult


# TODO implement and test
class ImageAnalyzerEngine:
    """ImageAnalyzerEngine class."""

    def analyse(self, image: object) -> List[ImageRecognizerResult]:
        """Analyse method to analyse the given image.

        :param image: PIL Image/numpy array or file path(str) to be processed

        :return: list of the extract entities with image bounding boxes
        """
        pass

    def map_entities(
        self, text_analyzer: RecognizerResult, ocr_result: dict
    ) -> List[ImageRecognizerResult]:
        """Map extracted PII entities to image bounding boxes.

        :param text_analyzer: PII entities recognized by presidio analyzer
        :param ocr_results: dict results with words and bboxes from OCR

        return: list of extracted entities with image bounding boxes
        """
        pass
