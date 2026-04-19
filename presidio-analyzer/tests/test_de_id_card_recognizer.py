"""
Tests for DeIdCardRecognizer (Personalausweisnummer).

Covers two formats:
  - nPA (since Nov 2010): 9 chars = 8 ICAO-charset chars + 1 check digit
    (ICAO Doc 9303 weights 7,3,1; letters A=10…Z=35; sum mod 10).
  - Legacy (pre-Nov 2010): T + 8 digits, no check digit.

Pre-calculated valid nPA examples (computed via the ICAO check):
  L01X00T44, C01234565, CZ6311T03, G00000002
Legacy examples remain accepted at pattern confidence without checksum.
"""
import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import DeIdCardRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeIdCardRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_ID_CARD"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # fmt: off
        # --- nPA format with valid ICAO check digit ---
        ("L01X00T44", 1, ((0, 9),)),
        ("C01234565", 1, ((0, 9),)),
        ("CZ6311T03", 1, ((0, 9),)),
        ("G00000002", 1, ((0, 9),)),
        # In running text
        ("Personalausweis: L01X00T44.", 1, ((17, 26),)),
        # Lowercase — IGNORECASE, validate_result uppercases
        ("l01x00t44",  1, ((0, 9),)),
        # --- Legacy T-format (pre-Nov 2010, no ICAO check digit) ---
        ("T22000129", 1, ((0, 9),)),
        ("T00000000", 1, ((0, 9),)),
        ("T99999999", 1, ((0, 9),)),
        ("Ausweis Nr. T22000129 gültig bis 2025.", 1, ((12, 21),)),
        ("t22000129", 1, ((0, 9),)),
        # --- Invalid cases ---
        # nPA-shaped but wrong ICAO check → dropped
        ("L01X00T47", 0, ()),
        ("C01234567", 0, ()),
        # Too short / too long
        ("T2200012",  0, ()),
        ("T220001290", 0, ()),
        # All digits in 9-char form → no first-letter match
        ("123456789", 0, ()),
        # fmt: on
    ],
)
def test_when_all_de_id_cards_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len


@pytest.mark.parametrize(
    "number, expected",
    [
        # Valid ICAO nPA
        ("L01X00T44", True),
        ("C01234565", True),
        ("CZ6311T03", True),
        ("G00000002", True),
        # Lowercase — upper() path
        ("l01x00t44", True),
        # Invalid ICAO check
        ("L01X00T47", False),
        ("C01234567", False),
        # Legacy T + 8 digits → None (accepted at pattern score only)
        ("T22000129", None),
        ("T00000000", None),
        # Wrong length
        ("L01X00T4",  False),
        ("L01X00T440", False),
        # Last char must be digit (for nPA form)
        ("L01X00T4A", False),
    ],
)
def test_when_de_id_card_validated_then_checksum_result_is_correct(
    number, expected, recognizer
):
    assert recognizer.validate_result(number) == expected
