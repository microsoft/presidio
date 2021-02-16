from typing import List

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer import RecognizerResult
from presidio_image_redactor.entities.image_recognizer_result import (
    ImageRecognizerResult,
)
from presidio_image_redactor.ocr import OCR


class ImageAnalyzerEngine:
    """ImageAnalyzerEngine class."""

    def analyze(self, image: object, **kwargs) -> List[ImageRecognizerResult]:
        """Analyse method to analyse the given image.

        :param image: PIL Image/numpy array or file path(str) to be processed

        :return: list of the extract entities with image bounding boxes
        """
        ocr_result = OCR().perform_ocr(image)
        text = OCR().get_text_from_ocr_dict(ocr_result)

        analyzer = AnalyzerEngine()
        analyzer_result = analyzer.analyze(text=text, language="en", **kwargs)
        bboxes = self.map_analyzer_results_to_bounding_boxes(
            analyzer_result, ocr_result, text
        )
        return bboxes

    @staticmethod
    def map_analyzer_results_to_bounding_boxes(
        text_analyzer_results: List[RecognizerResult], ocr_result: dict, text: str
    ) -> List[ImageRecognizerResult]:
        """Map extracted PII entities to image bounding boxes.

        Matching is based on the position of the recognized entity from analyzer
        and word (in ocr dict) in the text.

        :param text_analyzer_results: PII entities recognized by presidio analyzer
        :param ocr_result: dict results with words and bboxes from OCR
        :param text: text the results are based on

        return: list of extracted entities with image bounding boxes
        """
        if (not ocr_result) or (not text_analyzer_results):
            return []

        bboxes = []
        proc_indexes = 0
        indexes = len(text_analyzer_results)

        pos = 0
        iter_ocr = enumerate(ocr_result["text"])
        for index, word in iter_ocr:
            if not word:
                pos += 1
            else:
                for element in text_analyzer_results:
                    text_element = text[element.start : element.end]
                    # check position and text of ocr word matches recognized entity
                    if (
                        max(pos, element.start) < min(element.end, pos + len(word))
                    ) and ((text_element in word) or (word in text_element)):
                        bboxes.append(
                            ImageRecognizerResult(
                                element.entity_type,
                                element.start,
                                element.end,
                                element.score,
                                ocr_result["left"][index],
                                ocr_result["top"][index],
                                ocr_result["width"][index],
                                ocr_result["height"][index],
                            )
                        )

                        # add bounding boxes for all words in ocr dict
                        # contained within the text of recognized entity
                        # based on relative position in the full text
                        while pos + len(word) < element.end:
                            index, word = next(iter_ocr)
                            if word:
                                bboxes.append(
                                    ImageRecognizerResult(
                                        element.entity_type,
                                        element.start,
                                        element.end,
                                        element.score,
                                        ocr_result["left"][index],
                                        ocr_result["top"][index],
                                        ocr_result["width"][index],
                                        ocr_result["height"][index],
                                    )
                                )
                            pos += len(word) + 1
                        proc_indexes += 1

                if proc_indexes == indexes:
                    break
                pos += len(word) + 1

        return bboxes
