"""Image Anonymizer root module."""
import logging

from .image_analyzer_engine import ImageAnalyzerEngine
from .image_anonymizer_engine import ImageAnonymizerEngine
from .ocr import OCR

# Set up default logging (with NullHandler)
logging.getLogger("presidio-image-anonymizer").addHandler(logging.NullHandler())

__all__ = [
    "OCR",
    "ImageAnalyzerEngine",
    "ImageAnonymizerEngine",
]
