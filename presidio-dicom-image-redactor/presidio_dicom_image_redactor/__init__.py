"""Image Redactor root module."""
import logging

from .dicom_image_redactor_engine import DicomImageRedactorEngine

# Set up default logging (with NullHandler)
logging.getLogger("presidio-dicom-image-redactor").addHandler(logging.NullHandler())

__all__ = [
    "DicomImageRedactorEngine",
]
