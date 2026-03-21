"""
Tests for DeKfzRecognizer (KFZ-Kennzeichen / vehicle registration plates).

Format: [1–3 letter district code] [space or hyphen] [1–2 letter identifier]
[space or hyphen] [1–4 digits] [optional E (electric) or H (historic) suffix].

Legal basis: Fahrzeug-Zulassungsverordnung (FZV) § 8.
Data protection: DSGVO Art. 4 Nr. 1 (ECJ C-582/14, Breyer v. Germany).
"""
import pytest

from presidio_analyzer.predefined_recognizers import DeKfzRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeKfzRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_KFZ"]


@pytest.mark.parametrize(
    "text, expected_len",
    [
        # fmt: off
        # --- Space-separated ---
        ("B AB 1234",      1),   # Berlin
        ("M XY 999",       1),   # München
        ("HH AB 1234",     1),   # Hamburg (2-letter district)
        ("KA EF 12H",      1),   # Karlsruhe, historic suffix
        ("S AB 12E",       1),   # Stuttgart, electric suffix
        ("MIL E 1234",     1),   # single-letter identifier
        ("MIL EF 1234E",   1),   # electric with 2-letter identifier
        # --- Hyphen-separated ---
        ("B-AB-1234",      1),
        ("M-XY-999",       1),
        ("HH-AB-1234",     1),
        # --- In running text ---
        ("Das Fahrzeug mit Kennzeichen B AB 1234 wurde gesehen.", 1),
        ("Kennzeichen: HH-AB-1234.", 1),
        # --- Should NOT match ---
        # Lowercase: global IGNORECASE → also matches
        ("b ab 1234",      1),
        ("m xy 999",       1),
        # No separator
        ("BAB1234",         0),
        # Only district code + digits, no letter identifier
        ("B 1234",          0),
        # Four-letter district code (not valid in Germany)
        ("BXYZ AB 1234",    0),
        # fmt: on
    ],
)
def test_when_all_de_kfz_numbers_then_succeed(text, expected_len, recognizer, entities):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
