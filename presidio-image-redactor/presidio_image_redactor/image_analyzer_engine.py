from typing import List, Tuple, Optional

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

    def analyze(
        self, image: object, ocr_kwargs: Optional[dict] = None, **text_analyzer_kwargs
    ) -> List[ImageRecognizerResult]:
        """Analyse method to analyse the given image.

        :param image: PIL Image/numpy array or file path(str) to be processed.
        :param ocr_kwargs: Additional params for OCR methods.
        :param text_analyzer_kwargs: Additional values for the analyze method
        in AnalyzerEngine.

        :return: List of the extract entities with image bounding boxes.
        """
        # Perform OCR
        perform_ocr_kwargs, ocr_threshold = self._parse_ocr_kwargs(ocr_kwargs)
        ocr_result = self.ocr.perform_ocr(image, **perform_ocr_kwargs)
        ocr_result = self.remove_space_boxes(ocr_result)

        # Apply OCR confidence threshold if it is passed in
        if ocr_threshold:
            ocr_result = self.threshold_ocr_result(ocr_result, ocr_threshold)

        # Analyze text
        text = self.ocr.get_text_from_ocr_dict(ocr_result)

        analyzer_result = self.analyzer_engine.analyze(
            text=text, language="en", **text_analyzer_kwargs
        )
        allow_list = self._check_for_allow_list(text_analyzer_kwargs)
        bboxes = self.map_analyzer_results_to_bounding_boxes(
            analyzer_result, ocr_result, text, allow_list
        )
        return bboxes

    @staticmethod
    def threshold_ocr_result(ocr_result: dict, ocr_threshold: float) -> dict:
        """Filter out OCR results below confidence threshold.

        :param ocr_result: OCR results (raw).
        :param ocr_threshold: Threshold value between -1 and 100.

        :return: OCR results with low confidence items removed.
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
    def remove_space_boxes(ocr_result: dict) -> dict:
        """Remove OCR bboxes that are for spaces.

        :param ocr_result: OCR results (raw or thresholded).
        :return: OCR results with empty words removed.
        """
        # Get indices of items with no text
        idx = list()
        for i, text in enumerate(ocr_result["text"]):
            is_not_space = text.isspace() is False
            if text != "" and is_not_space:
                idx.append(i)

        # Only retain items with text
        filtered_ocr_result = {}
        for key in list(ocr_result.keys()):
            filtered_ocr_result[key] = [ocr_result[key][i] for i in idx]

        return filtered_ocr_result

    @staticmethod
    def map_analyzer_results_to_bounding_boxes(
        text_analyzer_results: List[RecognizerResult],
        ocr_result: dict,
        text: str,
        allow_list: List[str],
    ) -> List[ImageRecognizerResult]:
        """Map extracted PII entities to image bounding boxes.

        Matching is based on the position of the recognized entity from analyzer
        and word (in ocr dict) in the text.

        :param text_analyzer_results: PII entities recognized by presidio analyzer
        :param ocr_result: dict results with words and bboxes from OCR
        :param text: text the results are based on
        :param allow_list: List of words to not redact

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
                        yes_make_bbox_for_word = (
                            (word is not None)
                            and (word != "")
                            and (word.isspace() is False)
                            and (word not in allow_list)
                        )
                        # Do not add bbox for standalone spaces / empty strings
                        if yes_make_bbox_for_word:
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
                                yes_make_bbox_for_word = (
                                    (word is not None)
                                    and (word != "")
                                    and (word.isspace() is False)
                                    and (word not in allow_list)
                                )
                                if yes_make_bbox_for_word:
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

    @staticmethod
    def _parse_ocr_kwargs(ocr_kwargs: dict) -> Tuple[dict, float]:
        """Parse the OCR-related kwargs.

        :param ocr_kwargs: Parameters for OCR operations.

        :return: Params for ocr.perform_ocr and ocr_threshold
        """
        ocr_threshold = None
        if ocr_kwargs is not None:
            if "ocr_threshold" in ocr_kwargs:
                ocr_threshold = ocr_kwargs["ocr_threshold"]
                ocr_kwargs = {
                    key: value
                    for key, value in ocr_kwargs.items()
                    if key != "ocr_threshold"
                }
        else:
            ocr_kwargs = {}

        return ocr_kwargs, ocr_threshold

    @staticmethod
    def _check_for_allow_list(text_analyzer_kwargs: dict) -> List[str]:
        """Check the text_analyzer_kwargs for an allow_list.

        :param text_analyzer_kwargs: Text analyzer kwargs.
        :return: The allow list if it exists.
        """
        allow_list = []
        if text_analyzer_kwargs is not None:
            if "allow_list" in text_analyzer_kwargs:
                allow_list = text_analyzer_kwargs["allow_list"]

        return allow_list
