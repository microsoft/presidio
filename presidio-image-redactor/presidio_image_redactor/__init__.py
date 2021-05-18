"""Image Redactor root module."""
import logging

from .ocr import OCR
from .tesseract_ocr import TesseractOCR
from .image_analyzer_engine import ImageAnalyzerEngine
from .image_redactor_engine import ImageRedactorEngine
from .image_pii_verify_engine import ImagePiiVerifyEngine

# Set up default logging (with NullHandler)
logging.getLogger("presidio-image-redactor").addHandler(logging.NullHandler())

__all__ = [
    "OCR",
    "TesseractOCR",
    "ImageAnalyzerEngine",
    "ImageRedactorEngine",
    "ImagePiiVerifyEngine",
]
