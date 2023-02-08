from abc import ABC, abstractmethod
from typing import Tuple, List, Optional
import cv2


class QRRecognizerResult:
    """
    QRRecognizerResult represents the results of analysing the image
    by QRRecognizer.

    :param text: decoded text
    :param bbox: bounding box in the following format - [left, top, width, height]
    :param polygon: polygon aroung qr code
    """

    def __init__(
        self,
        text: str,
        bbox: Tuple[int, int, int, int],
        polygon: Optional[List[Tuple[int, int]]] = None
    ):
        self.text = text
        self.bbox = bbox
        self.polygon = polygon


class QRRecognizer(ABC):
    """
    QRRecognizer is an abstract class to be inherited by
    recognizers which hold the logic for recognizing qr codes on the images.
    """

    @abstractmethod
    def recognize(self, image) -> List[QRRecognizerResult]:
        """Detects and decodes QR codes on the image.

        :param image: PIL Image/numpy array to be processed
        """
        pass

