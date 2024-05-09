"""Image Redactor root module."""

import logging

from .bbox import BboxProcessor
from .dicom_image_pii_verify_engine import DicomImagePiiVerifyEngine
from .dicom_image_redactor_engine import DicomImageRedactorEngine
from .document_intelligence_ocr import DocumentIntelligenceOCR
from .image_analyzer_engine import ImageAnalyzerEngine
from .image_pii_verify_engine import ImagePiiVerifyEngine
from .image_processing_engine import (
    BilateralFilter,
    ContrastSegmentedImageEnhancer,
    ImagePreprocessor,
    ImageRescaling,
    SegmentedAdaptiveThreshold,
)
from .image_redactor_engine import ImageRedactorEngine
from .ocr import OCR
from .tesseract_ocr import TesseractOCR

# Set up default logging (with NullHandler)
logging.getLogger("presidio-image-redactor").addHandler(logging.NullHandler())

__all__ = [
    "OCR",
    "TesseractOCR",
    "DocumentIntelligenceOCR",
    "BboxProcessor",
    "ImageAnalyzerEngine",
    "ImageRedactorEngine",
    "ImagePreprocessor",
    "ImagePiiVerifyEngine",
    "DicomImageRedactorEngine",
    "DicomImagePiiVerifyEngine",
    "ContrastSegmentedImageEnhancer",
    "BilateralFilter",
    "SegmentedAdaptiveThreshold",
    "ImageRescaling",
]
