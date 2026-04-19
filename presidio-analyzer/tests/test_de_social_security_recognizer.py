"""
Tests for DeSocialSecurityRecognizer (Rentenversicherungsnummer / RVNR).

Format: 12 characters – 8 digits (area + birth date) + 1 uppercase letter
(birth surname initial) + 2 digits (serial) + 1 check digit.

Valid numbers are generated with the VKVV § 4 checksum algorithm:
letter expanded to 2-digit ordinal (A=01…Z=26), weights
[2,1,2,5,7,1,2,1,2,1,2,1] on the 12 effective digits, cross-sum per
product, sum mod 10.

Legal basis: § 147 SGB VI; VKVV § 4.

Pre-calculated valid examples:
  15070649C103  – canonical DRV example (area 15, 07.06.1949, C, serial 10, check 3)
  65070803A019  – area 65 (BaWü), 08.07.2003, A, serial 01, check 9
  20151090B023  – area 20 (Westfalen-Lippe), 15.10.1990, B, serial 02, check 3
  38551285K051  – Ergänzungsmerkmal day (55=5+50), 12.1985, K, serial 05, check 1
"""
import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import DeSocialSecurityRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeSocialSecurityRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_SOCIAL_SECURITY"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # fmt: off
        # Valid RVNR – checksum passes → result at MAX_SCORE
        ("15070649C103", 1, ((0, 12),)),
        ("65070803A019", 1, ((0, 12),)),
        ("20151090B023", 1, ((0, 12),)),
        ("38551285K051", 1, ((0, 12),)),
        ("RVNR: 15070649C103 laut Sozialversicherungsausweis.", 1, ((6, 18),)),
        # Invalid: wrong check digit
        ("15070649C100", 0, ()),
        ("65070803A012", 0, ()),
        # Invalid: invalid month (00 or 13+)
        ("15070049C103", 0, ()),
        ("15071349C103", 0, ()),
        # Invalid: digit at position 9 instead of letter
        ("150706491103", 0, ()),
        # Too short / too long
        ("15070649C10",  0, ()),
        ("15070649C1030", 0, ()),
        # fmt: on
    ],
)
def test_when_all_de_social_security_numbers_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)


@pytest.mark.parametrize(
    "number, expected",
    [
        # Valid — VKVV § 4 canonical example
        ("15070649C103", True),
        ("65070803A019", True),
        ("20151090B023", True),
        ("38551285K051", True),
        # Wrong check digit
        ("15070649C100", False),
        ("65070803A012", False),
        ("65070803A018", False),  # old fixture: was "valid" under wrong algorithm
        # Digit instead of letter at position 9
        ("150706491103", False),
        # Wrong length
        ("15070649C10",  False),
        ("15070649C1030", False),
    ],
)
def test_when_de_social_security_validated_then_checksum_result_is_correct(
    number, expected, recognizer
):
    assert recognizer.validate_result(number) == expected
