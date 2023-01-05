from typing import List, Optional

from presidio_analyzer import AnalyzerEngine, RecognizerResult

from presidio_image_redactor import OCR, TesseractOCR
from presidio_image_redactor.entities import ImageRecognizerResult


class ImageAnalyzerEngine:
    """ImageAnalyzerEngine class.

    :param analyzer_engine: The Presidio AnalyzerEngine instance
        to be used to detect PII in text
    :param ocr: the OCR object to be used to detect text in images.
    """

    def __init__(
        self,
        analyzer_engine: Optional[AnalyzerEngine] = None,
        ocr: Optional[OCR] = None,
    ):
        if not analyzer_engine:
            analyzer_engine = AnalyzerEngine()
        self.analyzer_engine = analyzer_engine

        if not ocr:
            ocr = TesseractOCR()
        self.ocr = ocr

    def analyze(self, image: Optional[object], **kwargs) -> List[ImageRecognizerResult]:
        """Analyse method to analyse the given image.

        :param image: PIL Image/numpy array or file path(str) to be processed
        :param kwargs: Additional values for the analyze method in AnalyzerEngine

        :return: list of the extract entities with image bounding boxes
        """
        ocr_result = self.ocr.perform_ocr(image)

        # Apply OCR confidence threshold if it is passed in
        if "ocr_threshold" in kwargs:
            ocr_result = self.threshold_ocr_result(ocr_result, kwargs["ocr_threshold"])
            kwargs = {
                key: value for key, value in kwargs.items() if key != "ocr_threshold"
            }

        text = self.ocr.get_text_from_ocr_dict(ocr_result)

        analyzer_result = self.analyzer_engine.analyze(
            text=text, language="en", **kwargs
        )
        bboxes = self.map_analyzer_results_to_bounding_boxes(
            analyzer_result, ocr_result, text
        )
        return bboxes

    @staticmethod
    def threshold_ocr_result(ocr_result: dict, ocr_threshold: float) -> dict:
        """Filter out OCR results below confidence threshold.

        Args:
            ocr_result (dict): OCR results (raw).
            ocr_threshold (float): Threshold value between -1 and 100.

        Return:
            filtered_ocr_result (dict): OCR results with low confidence items removed.
        """
        if ocr_threshold < -1 or ocr_threshold > 100:
            raise ValueError("ocr_threshold must be between -1 and 100")

        # Get indices of items above threshold
        idx = list()
        for i, val in enumerate(ocr_result["conf"]):
            if float(val) >= ocr_threshold:
                idx.append(i)

        # Only retain high confidence items
        filtered_ocr_result = {}
        for key in list(ocr_result.keys()):
            filtered_ocr_result[key] = [ocr_result[key][i] for i in idx]

        return filtered_ocr_result

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
                            prev_word = word
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
                            pos += len(prev_word) + 1
                        proc_indexes += 1

                if proc_indexes == indexes:
                    break
                pos += len(word) + 1

        return bboxes
