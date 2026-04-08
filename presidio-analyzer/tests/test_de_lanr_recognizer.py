"""
Tests for DeLanrRecognizer (Lebenslange Arztnummer / LANR).

Format: 9 digits — 6-digit physician identifier + 1 check digit + 2-digit
specialty code.  Check digit derived via KBV algorithm: weights [4,9,2,10,5,3]
on digits 1–6; cross-sum for products > 9; check = sum mod 10.

Legal basis: § 75 Abs. 7 SGB V; KBV-Richtlinie zur Vergabe der Arzt-,
Betriebsstätten-, Praxisnetz- sowie Netzverbundnummern.

Pre-calculated valid examples (fictitious):
  123456901  – physician 123456, check 9, specialty 01
  234567601  – physician 234567, check 6, specialty 01
  100000401  – physician 100000, check 4, specialty 01
  987654901  – physician 987654, check 9, specialty 01
  555555001  – physician 555555, check 0, specialty 01
"""
import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import DeLanrRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeLanrRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_LANR"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # fmt: off
        # Valid LANR – checksum passes → result at MAX_SCORE
        ("123456901", 1, ((0, 9),)),
        ("234567601", 1, ((0, 9),)),
        ("100000401", 1, ((0, 9),)),
        ("987654901", 1, ((0, 9),)),
        ("555555001", 1, ((0, 9),)),
        # Valid LANR in running text
        ("LANR: 123456901 des behandelnden Arztes.", 1, ((6, 15),)),
        ("Arztnummer 987654901 auf dem Rezept.", 1, ((11, 20),)),
        # Invalid: wrong check digit
        ("123456801", 0, ()),
        ("234567001", 0, ()),
        ("100000001", 0, ()),
        # Too short (8 digits) – word boundary prevents match
        ("12345690",  0, ()),
        # Too long (10 digits) – word boundary prevents match
        ("1234569010", 0, ()),
        # fmt: on
    ],
)
def test_when_all_de_lanr_numbers_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)


@pytest.mark.parametrize(
    "number, expected",
    [
        # Valid check digit
        ("123456901", True),
        ("234567601", True),
        ("100000401", True),
        ("987654901", True),
        ("555555001", True),
        # Wrong check digit
        ("123456801", False),
        ("234567001", False),
        ("100000101", False),
        # Wrong length
        ("12345690",  False),
        ("1234569010", False),
        # Non-numeric
        ("12345690a", False),
    ],
)
def test_when_de_lanr_validated_then_checksum_result_is_correct(
    number, expected, recognizer
):
    assert recognizer.validate_result(number) == expected
