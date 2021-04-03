from abc import ABC, abstractmethod


class OCR(ABC):
    """OCR class that performs OCR on a given image."""

    @abstractmethod
    def perform_ocr(self, image: object) -> dict:
        """Perform OCR on a given image.

        :param image: PIL Image/numpy array or file path(str) to be processed

        :return: results dictionary containing bboxes and text for each detected word
        """
        pass
