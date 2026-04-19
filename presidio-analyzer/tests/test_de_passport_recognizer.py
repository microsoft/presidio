"""
Tests for DePassportRecognizer (Reisepassnummer).

German passport numbers follow ICAO Doc 9303: 9 characters where the first
8 are from the restricted uppercase charset (excludes A, B, D, E, I, O, Q,
S, U) and the 9th is the ICAO check digit (weights 7,3,1; letters A=10…
Z=35; sum mod 10).

Legal basis: Passgesetz (PassG) § 4, Passverordnung (PassV).

Pre-calculated valid examples:
  C01234565  – computed from prefix C0123456 (check 5)
  F12345671  – computed from prefix F1234567 (check 1)
  L01X00T44  – computed from prefix L01X00T4 (check 4)
  CZ6311T03  – computed from prefix CZ6311T0 (check 3)
  G00000002  – all-zero stress test, check 2
"""
import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import DePassportRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DePassportRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_PASSPORT"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # fmt: off
        # Valid ICAO check digit → strict ICAO charset matches, validated
        ("C01234565", 1, ((0, 9),)),
        ("F12345671", 1, ((0, 9),)),
        ("L01X00T44", 1, ((0, 9),)),
        ("CZ6311T03", 1, ((0, 9),)),
        ("G00000002", 1, ((0, 9),)),
        # In running text
        ("Reisepass C01234565 ausgestellt am 01.01.2020.", 1, ((10, 19),)),
        ("Pass-Nr.: F12345671", 1, ((10, 19),)),
        # Invalid check digit — dropped
        ("C01234567", 0, ()),
        ("F12345678", 0, ()),
        ("L01X00T47", 0, ()),
        # Lowercase: global IGNORECASE, validate_result uppercases
        ("c01234565", 1, ((0, 9),)),
        # Too short (8 chars) / too long (10 chars)
        ("C0123456",  0, ()),
        ("C012345678", 0, ()),
        # Digits only → no match (first char must be letter)
        ("901234567", 0, ()),
        # fmt: on
    ],
)
def test_when_all_de_passports_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)


@pytest.mark.parametrize(
    "number, expected",
    [
        # Valid ICAO check digits
        ("C01234565", True),
        ("F12345671", True),
        ("L01X00T44", True),
        ("CZ6311T03", True),
        ("G00000002", True),
        # Lowercase — upper() path
        ("c01234565", True),
        # Invalid check digits
        ("C01234567", False),
        ("L01X00T47", False),
        # Wrong length
        ("C0123456", False),
        ("C012345678", False),
        # Last char must be digit
        ("C0123456A", False),
    ],
)
def test_when_de_passport_validated_then_checksum_result_is_correct(
    number, expected, recognizer
):
    assert recognizer.validate_result(number) == expected
