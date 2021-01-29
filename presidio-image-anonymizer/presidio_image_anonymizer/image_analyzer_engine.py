from typing import List
from presidio_image_anonymizer.image_recognizer_result import ImageRecognizerResult
from presidio_image_anonymizer.ocr import OCR
from presidio_analyzer import RecognizerResult
from presidio_analyzer import AnalyzerEngine


class ImageAnalyzerEngine:
    """ImageAnalyzerEngine class."""

    def analyze(self, image: object) -> List[ImageRecognizerResult]:
        """Analyse method to analyse the given image.

        :param image: PIL Image/numpy array or file path(str) to be processed

        :return: list of the extract entities with image bounding boxes
        """
        ocr_result = OCR().perform_ocr(image)
        text = self.get_text_from_ocr_dict(ocr_result)

        analyzer = AnalyzerEngine()
        analyzer_result = analyzer.analyze(text=text, language="en")
        bboxes = self.map_entities(analyzer_result, ocr_result, text)
        return bboxes

    @staticmethod
    def get_text_from_ocr_dict(ocr_result: dict, separator: str = " ") -> str:
        """Combine the text from the OCR dict to full text.

        :param ocr_result: dictionary containing the ocr results per word
        :param separator: separator to use when joining the words

        return: str containing the full extracted text as string
        """
        if not ocr_result:
            return ""
        elif "text" in ocr_result:
            text = separator.join(ocr_result["text"])
            return text
        else:
            raise KeyError("Key 'text' not found in dictionary")

    @staticmethod
    def map_entities(
        text_analyzer: RecognizerResult, ocr_result: dict, text: str
    ) -> List[ImageRecognizerResult]:
        """Map extracted PII entities to image bounding boxes.

        :param text_analyzer: PII entities recognized by presidio analyzer
        :param ocr_results: dict results with words and bboxes from OCR
        :param text: text the results are based on

        return: list of extracted entities with image bounding boxes
        """
        if not ocr_result:
            return []
        elif "text" not in ocr_result:
            raise KeyError("Key 'text' not found in dictionary")

        if not text_analyzer:
            return []

        bboxes = []
        proc_indexes = 0
        indexes = len(text_analyzer)

        pos = 0
        iter_ocr = enumerate(ocr_result["text"])
        for index, word in iter_ocr:
            if not word:
                pos += 1
            else:
                for element in text_analyzer:
                    text_element = text[element.start : element.end]
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
