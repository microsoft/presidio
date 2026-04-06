"""
Tests for DeHandelsregisterRecognizer (Handelsregisternummer).

The HR[AB] prefix makes the pattern highly specific, keeping false positives low.
Legal basis: §§ 9, 14 HGB; DSGVO Art. 4 Nr. 1 for HRA entries (sole traders).
"""
import pytest

from presidio_analyzer.predefined_recognizers import DeHandelsregisterRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeHandelsregisterRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_HANDELSREGISTER"]


@pytest.mark.parametrize(
    "text, expected_len",
    [
        # fmt: off
        # --- HRB (corporations) ---
        ("HRB 123456", 1),
        ("HRB 1",      1),   # minimum 1 digit
        ("HRB123456",  1),   # no space variant
        # --- HRA (sole traders / partnerships) ---
        ("HRA 12345",  1),
        ("HRA12345",   1),
        # In running text
        ("Amtsgericht München HRB 12345.", 1),
        ("eingetragen im HRA 99999 Köln", 1),
        ("Handelsregisternummer: HRB 123456", 1),
        # 6-digit maximum
        ("HRB 999999", 1),
        # --- Should NOT match ---
        # Wrong section letter
        ("HRC 12345",  0),
        ("HR 12345",   0),
        # Too many digits (> 6)
        ("HRB 1234567", 0),
        # Lowercase: global IGNORECASE → also matches
        ("hrb 12345",  1),
        # fmt: on
    ],
)
def test_when_all_de_handelsregister_numbers_then_succeed(
    text, expected_len, recognizer, entities
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
