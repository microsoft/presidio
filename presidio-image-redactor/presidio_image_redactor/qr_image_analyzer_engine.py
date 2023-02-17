from typing import List, Optional

from presidio_analyzer import AnalyzerEngine

from presidio_image_redactor.entities import ImageRecognizerResult
from presidio_image_redactor.qr_recognizer import QRRecognizer
from presidio_image_redactor.qr_recognizer import OpenCVQRRecongnizer


class QRImageAnalyzerEngine:
    """QRImageAnalyzerEngine class.

    :param analyzer_engine: The Presidio AnalyzerEngine instance
        to be used to detect PII in text
    :param qr: the QRRecognizer object to detect and decode text in QR codes
    """

    def __init__(
        self,
        analyzer_engine: Optional[AnalyzerEngine] = None,
        qr: Optional[QRRecognizer] = None,
    ):
        if not analyzer_engine:
            analyzer_engine = AnalyzerEngine()
        self.analyzer_engine = analyzer_engine

        if not qr:
            qr = OpenCVQRRecongnizer()
        self.qr = qr

    def analyze(
        self, image: object, **text_analyzer_kwargs
    ) -> List[ImageRecognizerResult]:
        """Analyse method to analyse the given image.

        :param image: PIL Image/numpy array to be processed.
        :param text_analyzer_kwargs: Additional values for the analyze method
        in AnalyzerEngine.

        :return: List of the extract entities with image bounding boxes.
        """
        bboxes = []

        qr_result = self.qr.recognize(image)
        for qr_code in qr_result:
            analyzer_result = self.analyzer_engine.analyze(
                text=qr_code.text, language="en", **text_analyzer_kwargs
            )
            for res in analyzer_result:
                bboxes.append(
                    ImageRecognizerResult(
                        res.entity_type,
                        res.start,
                        res.end,
                        res.score,
                        qr_code.bbox[0],
                        qr_code.bbox[1],
                        qr_code.bbox[2],
                        qr_code.bbox[3],
                    )
                )
        return bboxes
