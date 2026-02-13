import pydicom
from pydicom.multival import MultiValue

from presidio_image_redactor.dicom_image_redactor_engine import DicomImageRedactorEngine


def test_make_phi_list_flattens_trims_and_dedupes_without_mutation():
    # Simulate mixed metadata (strings, list, MultiValue, empty/None)
    meta = [
        "John Doe",
        ["Jane", "Doe", ""],
        MultiValue(str, ["X", "X", "Y"]),
        "",
        None,
    ]
    # First entry is_name, second is_patient, third is_name (to test MultiValue)
    is_name =    [True,  False, True,  False, False]
    is_patient = [False, True,  False, False, False]

    out = DicomImageRedactorEngine._make_phi_list(meta, is_name, is_patient)

    # Should be flattened, trimmed and stably de-duplicated
    # (allow for case/variant expansions produced by augment_word)
    required = {"John Doe", "Jane", "Doe", "X", "Y"}
    assert required.issubset(set(out))

    # No exact duplicates (stable dedupe)
    assert len(out) == len(set(out))

    # Ensure original metadata unchanged
    assert meta[1] == ["Jane", "Doe", ""]
    assert list(meta[2]) == ["X", "X", "Y"]
