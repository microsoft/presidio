"""Image Redactor root module."""
import logging

from .image_analyzer_engine import ImageAnalyzerEngine
from .image_redactor_engine import ImageRedactorEngine
from .image_pii_verify_engine import ImagePiiVerifyEngine
from .ocr import OCR

# Set up default logging (with NullHandler)
logging.getLogger("presidio-image-redactor").addHandler(logging.NullHandler())

__all__ = [
    "OCR",
    "ImageAnalyzerEngine",
    "ImageRedactorEngine",
    "ImagePiiVerifyEngine"
]
