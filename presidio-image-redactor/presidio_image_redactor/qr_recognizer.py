from abc import ABC, abstractmethod
from typing import Tuple, List, Optional
import cv2
import numpy as np


class QRRecognizerResult:
    """
    Represent the results of analysing the image by QRRecognizer.

    :param text: Decoded text
    :param bbox: Bounding box in the following format - [left, top, width, height]
    :param polygon: Polygon aroung QR code
    """

    def __init__(
        self,
        text: str,
        bbox: Tuple[int, int, int, int],
        polygon: Optional[List[int]] = None,
    ):
        self.text = text
        self.bbox = bbox
        self.polygon = polygon

    def __eq__(self, other):
        """
        Compare two QRRecognizerResult objects.

        :param other: another QRRecognizerResult object
        :return: bool
        """
        equal_text = self.text == other.text
        equal_bbox = self.bbox == other.bbox
        equal_polygon = self.polygon == other.polygon

        return equal_text and equal_bbox and equal_polygon

    def __repr__(self) -> str:
        """Return a string representation of the instance."""
        return (
            f"{type(self).__name__}("
            f"text={self.text}, "
            f"bbox={self.bbox}, "
            f"polygon={self.polygon})"
        )


class QRRecognizer(ABC):
    """
    A class representing an abstract QR code recognizer.

    QRRecognizer is an abstract class to be inherited by
    recognizers which hold the logic for recognizing QR codes on the images.
    """

    @abstractmethod
    def recognize(self, image: object) -> List[QRRecognizerResult]:
        """Detect and decode QR codes on the image.

        :param image: PIL Image/numpy array to be processed

        :return: List of the recognized QR codes
        """


class OpenCVQRRecongnizer(QRRecognizer):
    """
    QR code recognition using OpenCV.

    Example of the usage:
        from presidio_image_redactor import OpenCVQRRecognizer

        image = cv2.imread("qrcode.jpg")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        recognized = OpenCVQRRecongnizer().recognize(image)
    """

    def __init__(self) -> None:
        self.detector = cv2.QRCodeDetector()

    def recognize(self, image: object) -> List[QRRecognizerResult]:
        """Detect and decode QR codes on the image.

        :param image: PIL Image/numpy array to be processed

        :return: List of the recognized QR codes
        """

        if not isinstance(image, np.ndarray):
            image = np.array(image, dtype=np.uint8)

        recognized = []

        ret, points = self._detect(image)

        if ret:
            decoded = self._decode(image, points)

            for text, p in zip(decoded, points):
                (x, y, w, h) = cv2.boundingRect(p)

                recognized.append(
                    QRRecognizerResult(
                        text=text, bbox=[x, y, w, h], polygon=[*p.flatten(), *p[0]]
                    )
                )

        return recognized

    def _detect(self, image: object) -> Tuple[float, Optional[np.ndarray]]:
        """Detect QR codes on the image.

        :param image: Numpy array to be processed

        :return: Detection status and list of the points around QR codes
        """

        ret, points = self.detector.detectMulti(image)

        if not ret:
            ret, points = self.detector.detect(image)
        if points is not None:
            points = points.astype(int)

        return ret, points

    def _decode(self, image: object, points: np.ndarray) -> Tuple[str]:
        """Decode QR codes on the image.

        :param image: Numpy array to be processed
        :param points: Detected points

        :return: Tuple with decoded QR codes
        """

        if len(points) == 1:
            decoded, _ = self.detector.decode(image, points)
            decoded = (decoded,)
        else:
            _, decoded, _ = self.detector.decodeMulti(image, points)

        return decoded
