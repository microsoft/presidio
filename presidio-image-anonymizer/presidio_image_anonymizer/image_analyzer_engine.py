from typing import List
from presidio_image_anonymizer.image_recognizer_result import ImageRecognizerResult
from presidio_image_anonymizer.ocr import OCR
from presidio_analyzer import RecognizerResult
from presidio_analyzer import AnalyzerEngine
from collections import namedtuple


# TODO implement and test
class ImageAnalyzerEngine:
    """ImageAnalyzerEngine class."""

    def analyze(self, image: object) -> List[ImageRecognizerResult]:
        """Analyse method to analyse the given image.

        :param image: PIL Image/numpy array or file path(str) to be processed

        :return: list of the extract entities with image bounding boxes
        """
        result_dict = OCR().perform_ocr(image)
        text = self.get_text_from_ocr_dict(result_dict)

        analyzer = AnalyzerEngine()
        results = analyzer.analyze(text=text, language="en")
        Bbox = namedtuple(
            "Bbox",
            [
                "entity_type",
                "start_char",
                "end_char",
                "score",
                "left",
                "top",
                "width",
                "height",
            ],
        )
        bboxes = []

        for element in results:

            subtext = text[element.start : element.end]
            print(subtext)
            words = subtext.split(" ")

            for word in words:
                indexes = [
                    i
                    for i in range(len(result_dict["text"]))
                    if word in result_dict["text"][i]
                ]
                for index in indexes:
                    bboxes.append(
                        Bbox(
                            element.entity_type,
                            element.start,
                            element.end,
                            element.score,
                            result_dict["left"][index],
                            result_dict["top"][index],
                            result_dict["width"][index],
                            result_dict["height"][index],
                        )
                    )
        return bboxes

    @staticmethod
    def get_text_from_ocr_dict(ocr_result: dict) -> str:
        """Combine the text from the OCR dict to full text.

        :param ocr_result: dictionary containing the ocr results per word

        return: str containing the full extracted text as string
        """
        text = "This project"
        return text

    @staticmethod
    def map_entities(
        text_analyzer: RecognizerResult, ocr_result: dict
    ) -> List[ImageRecognizerResult]:
        """Map extracted PII entities to image bounding boxes.

        :param text_analyzer: PII entities recognized by presidio analyzer
        :param ocr_results: dict results with words and bboxes from OCR

        return: list of extracted entities with image bounding boxes
        """
        pass
