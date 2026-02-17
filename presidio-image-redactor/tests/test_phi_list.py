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


def test_process_names_excludes_non_flagged_entries():
    """Non-flagged metadata should never appear in _process_names output."""
    text_metadata = ["SMITH^JOHN", "City Hospital", "99999"]
    is_name = [True, False, False]

    result = DicomImageRedactorEngine._process_names(text_metadata, is_name)

    assert "City Hospital" not in result
    assert "99999" not in result
    assert "SMITH^JOHN" in result


def test_process_names_all_false_returns_empty():
    """When no flags are True, output should be empty."""
    text_metadata = ["foo", "bar", "baz"]
    is_name = [False, False, False]

    result = DicomImageRedactorEngine._process_names(text_metadata, is_name)

    assert result == []


def test_process_names_multivalue_iterated_individually():
    """MultiValue fields should be split into individual strings."""
    mv = MultiValue(str, ["1000", "234566"])
    text_metadata = [mv]
    is_name = [True]

    result = DicomImageRedactorEngine._process_names(text_metadata, is_name)

    assert "1000" in result
    assert "234566" in result
    # The stringified form should NOT be present
    assert "['1000', '234566']" not in result


def test_process_names_empty_and_whitespace_skipped():
    """Empty strings and whitespace-only items inside iterables are skipped."""
    text_metadata = [["Alice", "", "  "]]
    is_name = [True]

    result = DicomImageRedactorEngine._process_names(text_metadata, is_name)

    assert "Alice" in result
    # Empty / whitespace items should not be present
    assert "" not in result
    assert "  " not in result


def test_make_phi_list_non_flagged_metadata_excluded():
    """Metadata not flagged as name or patient should not appear in final PHI list."""
    meta = ["PATIENT^NAME", "Some Hospital", "Study Description"]
    is_name =    [True, False, False]
    is_patient = [False, False, False]

    out = DicomImageRedactorEngine._make_phi_list(meta, is_name, is_patient)

    assert "Some Hospital" not in out
    assert "Study Description" not in out
    assert "PATIENT^NAME" in out
