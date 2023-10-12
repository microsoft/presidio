import os
from io import BytesIO

from typing import Optional, Sequence

import numpy as np
from PIL import Image

from presidio_image_redactor import OCR

from azure.ai.formrecognizer import DocumentAnalysisClient, \
                                    AnalyzedDocument, \
                                    DocumentPage, \
                                    Point
from azure.core.credentials import AzureKeyCredential


class DocumentIntelligenceOCR(OCR):
    """OCR class that uses Microsoft's Document Intelligence OCR engine."""

    SUPPORTED_MODELS = [
        "prebuilt-document",
        "prebuilt-read",
        "prebuilt-layout",
        "prebuilt-contract",
        "prebuilt-healthInsuranceCard.us",
        "prebuilt-invoice",
        "prebuilt-receipt",
        "prebuilt-idDocument",
        "prebuilt-businessCard"
    ]

    def __init__(self,
                 endpoint: Optional[str] = None,
                 key: Optional[str] = None,
                 model_id: Optional[str] = "prebuilt-document"):
        if model_id not in DocumentIntelligenceOCR.SUPPORTED_MODELS:
            raise ValueError("Unsupported model id: %s" % model_id)

        # If endpoint and/or key are not passed, attempt to get from environment
        # variables
        if not endpoint:
            endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")

        if not key:
            key = os.getenv("DOCUMENT_INTELLIGENCE_KEY")

        if not key or not endpoint:
            raise ValueError("Endpoint and key must be specified")

        self.client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
        self.model_id = model_id

    @staticmethod
    def _polygon_to_bbox(polygon : Sequence[Point]) -> tuple:
        # Returns a tuple of left/top/width/height according to expected which covers
        # the passed polygon.

        # We need at least two points for a valid bounding box.
        if len(polygon) < 2:
            return (0, 0, 0, 0)

        left = min([int(p.x) for p in polygon])
        top = min([int(p.y) for p in polygon])
        right = max([int(p.x) for p in polygon])
        bottom = max([int(p.y) for p in polygon])
        width = right - left
        height = bottom - top
        return (left, top, width, height)

    @staticmethod
    def _page_to_bboxes(page: DocumentPage) -> dict:
        """Convert bounding boxes to uniform format."""
        # Presidio supports tesseract format of output only, so we format in the same
        # way.
        #
        # Expected format looks like:
        # {
        #     "left": [123, 345],
        #     "top": [0, 15],
        #     "width": [100, 75],
        #     "height": [25, 30],
        #     "conf": ["1", "0.87"],
        #     "text": ["JOHN", "DOE"],
        # }
        bounds = [DocumentIntelligenceOCR._polygon_to_bbox(word.polygon)
                  for word in page.words]

        return {
            "left": [box[0] for box in bounds],
            "top": [box[1] for box in bounds],
            "width": [box[2] for box in bounds],
            "height": [box[3] for box in bounds],
            "conf": [w.confidence for w in page.words],
            "text": [w.content for w in page.words]
        }

    def get_imgbytes(self, image: object, **kwargs) -> bytes:
        """Get the image bytes from the image object."""
        if isinstance(image, bytes):
            return image
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
            # Fallthrough to process PIL image
        if isinstance(image, Image.Image):
            # Image is a PIL image, write to bytes stream
            ostream = BytesIO()
            image.save(ostream, 'PNG')
            imgbytes = ostream.getvalue()
        elif isinstance(image, str):
            # image is a filename
            imgbytes = open(image, "rb")
        else:
            raise ValueError("Unsupported image type: %s" % type(image))
        return imgbytes

    def analyze_document(self, imgbytes : bytes, **kwargs) -> AnalyzedDocument:
        """Analyze the document and return the result."""
        poller = self.client.begin_analyze_document(self.model_id, imgbytes, **kwargs)
        return poller.result()

    def perform_ocr(self, image: object, **kwargs) -> dict:
        """Perform OCR on the image.

        :param image: PIL Image/numpy array or file path(str) to be processed
        :param kwargs: Additional values for begin_analyze_document

        :return: results dictionary containing bboxes and text for each detected word
        """
        imgbytes = self.get_imgbytes(image)
        result = self.analyze_document(imgbytes, **kwargs)

        # Currently cannot handle more than one page.
        if not (len(result.pages) == 1):
            raise ValueError("DocumentIntelligenceOCR only supports 1 page documents")

        return DocumentIntelligenceOCR._page_to_bboxes(result.pages[0])
