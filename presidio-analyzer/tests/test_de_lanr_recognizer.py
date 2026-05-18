"""
Tests for DeLanrRecognizer (Lebenslange Arztnummer / LANR).

Format: 9 digits — 6-digit physician identifier + 1 check digit + 2-digit
specialty code.  Check digit derived via KBV Arztnummern-Richtlinie:
weights [4,9,4,9,4,9] on digits 1–6 (no cross-sum), sum of products,
check = (10 − sum mod 10) mod 10.

Legal basis: § 75 Abs. 7 SGB V; KBV Arztnummern-Richtlinie.

Pre-calculated valid examples:
  123456601  – KBV canonical example (physician 123456, check 6)
  234567701  – physician 234567, check 7
  100000601  – physician 100000, check 6
  987654401  – physician 987654, check 4
  555555501  – physician 555555, check 5
  999999901  – physician 999999, check 9 (all-9 edge case)
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
        # Valid LANR – KBV-spec check digits
        ("123456601", 1, ((0, 9),)),
        ("234567701", 1, ((0, 9),)),
        ("100000601", 1, ((0, 9),)),
        ("987654401", 1, ((0, 9),)),
        ("555555501", 1, ((0, 9),)),
        ("999999901", 1, ((0, 9),)),
        # Valid LANR in running text
        ("LANR: 123456601 des behandelnden Arztes.", 1, ((6, 15),)),
        ("Arztnummer 987654401 auf dem Rezept.", 1, ((11, 20),)),
        # Invalid: wrong check digit (old fixtures from buggy algorithm)
        ("123456901", 0, ()),
        ("234567601", 0, ()),
        ("100000401", 0, ()),
        # Too short (8 digits)
        ("12345660",  0, ()),
        # Too long (10 digits)
        ("1234566010", 0, ()),
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
        # Valid — KBV canonical and derived examples
        ("123456601", True),
        ("234567701", True),
        ("100000601", True),
        ("987654401", True),
        ("555555501", True),
        ("999999901", True),
        # Wrong check digit — these were "valid" under the previous buggy algorithm
        ("123456901", False),
        ("234567601", False),
        ("100000401", False),
        # Wrong length
        ("12345660",  False),
        ("1234566010", False),
        # Non-numeric
        ("12345660a", False),
    ],
)
def test_when_de_lanr_validated_then_checksum_result_is_correct(
    number, expected, recognizer
):
    assert recognizer.validate_result(number) == expected
