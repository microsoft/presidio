import pytest
import pydicom
import numpy as np
from presidio_image_redactor.dicom_image_redactor_engine import DicomImageRedactorEngine
from presidio_image_redactor.image_analyzer_engine import ImageAnalyzerEngine  # NEW

def test_engine_initializes():
    engine = DicomImageRedactorEngine()
    assert engine is not None

def test_multi_frame_grayscale_dicom_handling(monkeypatch):  # <-- add monkeypatch
    # --- Mock OCR so no Tesseract is required ---
    monkeypatch.setattr(
        ImageAnalyzerEngine,
        "analyze",
        lambda self, image, **kwargs: []   # empty detections
    )

    pixel_array = np.random.randint(0, 256, (3, 64, 64), dtype=np.uint8)

    file_meta = pydicom.dataset.FileMetaDataset()
    from pydicom.uid import ExplicitVRLittleEndian
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian

    ds = pydicom.dataset.FileDataset("test", {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.Rows = 64
    ds.Columns = 64
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.NumberOfFrames = pixel_array.shape[0]
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.PixelRepresentation = 0
    ds.PixelData = pixel_array.tobytes()
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    engine = DicomImageRedactorEngine()
    redacted, bboxes = engine.redact_and_return_bbox(ds)

    assert redacted is not None
    assert isinstance(redacted, pydicom.dataset.FileDataset)
    assert isinstance(bboxes, list)
