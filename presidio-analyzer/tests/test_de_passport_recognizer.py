"""
Tests for DePassportRecognizer (Reisepassnummer).

German passport numbers follow ICAO Doc 9303: 9 alphanumeric characters
using a restricted uppercase character set (excludes I, O, Q, S, U).
Legal basis: Passgesetz (PassG) § 4, Passverordnung (PassV).

Note: Presidio applies global regex_flags=26 (IGNORECASE|MULTILINE|DOTALL),
so lowercase inputs also match the patterns.
"""
import pytest

from presidio_analyzer.predefined_recognizers import DePassportRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DePassportRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_PASSPORT"]


@pytest.mark.parametrize(
    "text, expected_len",
    [
        # fmt: off
        # --- Strict ICAO charset pattern (1 ICAO-letter + 7 ICAO-chars + 1 digit) ---
        ("C01234567",  1),   # starts with C, ends with digit
        ("F12345678",  1),
        # L01X00T47: L ∈ ICAO set, all inner chars valid, ends with digit 7 → matches
        ("L01X00T47",  1),
        # --- Relaxed pattern (any letter + 7 alphanumeric + 1 digit) ---
        ("A01234567",  1),
        ("Z98765432",  1),
        # In running text
        ("Reisepass C01234567 ausgestellt am 01.01.2020.", 1),
        ("Pass-Nr.: F12345678", 1),
        # Too short (8 chars)
        ("C0123456",   0),
        # Too long (10 chars) → word boundary prevents match
        ("C012345678",  0),
        # Lowercase: global IGNORECASE → also matches
        ("c01234567",  1),
        # Digits only → no match (first char must be letter)
        ("901234567",  0),
        # fmt: on
    ],
)
def test_when_all_de_passports_then_succeed(text, expected_len, recognizer, entities):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
