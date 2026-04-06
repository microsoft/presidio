"""
Tests for DeTaxNumberRecognizer (Steuernummer).

Tests cover both the ELSTER unified 13-digit format and the various
state-specific slash-separated formats used across German Bundesländer.
"""
import pytest

from presidio_analyzer.predefined_recognizers import DeTaxNumberRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeTaxNumberRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_TAX_NUMBER"]


@pytest.mark.parametrize(
    "text, expected_len",
    [
        # fmt: off
        # --- ELSTER unified 13-digit format (valid Bundesland codes 01–16) ---
        ("0281508150123", 1),   # Hamburg (02)
        ("0981508150999", 1),   # Bayern (09)
        ("1681508150001", 1),   # Thüringen (16)
        ("0181508150000", 1),   # Schleswig-Holstein (01)
        # Invalid Bundesland codes
        ("1781508150001", 0),   # code 17 does not exist
        ("0081508150001", 0),   # code 00 does not exist
        # Too short for 13-digit pattern
        ("028150815012",  0),
        # --- Slash-separated Bayern-style (3/3/5) ---
        ("123/456/78901", 1),
        ("987/654/32100", 1),
        # --- General slash-separated (2-3 / 3-4 / 4-5 digits) ---
        ("12/345/6789",   1),
        ("12/3456/7890",  1),
        ("123/3456/7890", 1),
        # Matches in running text
        ("Steuernummer: 0981508150999 wurde vergeben.", 1),
        ("St.-Nr. 123/456/78901 bitte angeben.",        1),
        # fmt: on
    ],
)
def test_when_all_de_tax_numbers_then_succeed(text, expected_len, recognizer, entities):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
