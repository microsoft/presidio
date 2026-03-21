"""
Tests for DeIdCardRecognizer (Personalausweisnummer).

Covers both the old format (T + 8 digits, pre-November 2010) and the
new nPA format (9 ICAO-compliant alphanumeric characters, since Nov 2010).
Legal basis: Personalausweisgesetz (PAuswG), Personalausweisverordnung (PAuswV).
"""
import pytest

from presidio_analyzer.predefined_recognizers import DeIdCardRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeIdCardRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_ID_CARD"]


@pytest.mark.parametrize(
    "text, expected_len",
    [
        # fmt: off
        # --- Old format: T + 8 digits (high confidence 0.5) ---
        ("T22000129",  1),
        ("T00000000",  1),
        ("T99999999",  1),
        ("Ausweis Nr. T22000129 gültig bis 2025.", 1),
        # --- nPA format: ICAO letter + 8 ICAO chars ---
        ("L01X00T47",  1),   # starts with L (valid ICAO)
        ("C01234567",  1),   # starts with C
        # In running text
        ("Personalausweis: L01X00T47.", 1),
        # --- Invalid cases ---
        # Lowercase: global IGNORECASE → also matches
        ("t22000129",  1),
        ("l01x00t47",  1),
        # Too short (8 chars)
        ("T2200012",   0),
        # Too long for any pattern (10+ chars without word boundary break)
        ("T220001290",  0),
        # Digits only with wrong length
        ("123456789",  0),
        # fmt: on
    ],
)
def test_when_all_de_id_cards_then_succeed(text, expected_len, recognizer, entities):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
