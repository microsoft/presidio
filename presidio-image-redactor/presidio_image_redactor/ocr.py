from abc import ABC, abstractmethod


class OCR(ABC):
    """OCR class that performs OCR on a given image."""

    @abstractmethod
    def perform_ocr(self, image: object, **kwargs) -> dict:
        """Perform OCR on a given image.

        :param image: PIL Image/numpy array or file path(str) to be processed
        :param kwargs: Additional values for perform OCR method

        :return: results dictionary containing bboxes and text for each detected word
        """
        pass

    @staticmethod
    def get_text_from_ocr_dict(ocr_result: dict, separator: str = " ") -> str:
        """Combine the text from the OCR dict to full text.

        :param ocr_result: dictionary containing the ocr results per word
        :param separator: separator to use when joining the words

        return: str containing the full extracted text as string
        """
        if not ocr_result:
            return ""
        else:
            return separator.join(ocr_result["text"])
