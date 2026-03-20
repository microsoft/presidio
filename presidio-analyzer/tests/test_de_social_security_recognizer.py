"""
Tests for DeSocialSecurityRecognizer (Rentenversicherungsnummer / RVNR).

Format: 12 characters – 8 digits (area + birth date) + 1 uppercase letter
(birth surname initial) + 2 digits (serial) + 1 check digit.

Valid numbers are generated with the official Deutsche Rentenversicherung
checksum algorithm (letter expanded to 2-digit ordinal, weights [2,1,...],
products digit-summed if ≥ 10, sum mod 10).

Legal basis: § 147 SGB VI.
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
        ("65070803A018", 1, ((0, 12),)),
        ("RVNR: 65070803A018 laut Sozialversicherungsausweis.", 1, ((6, 18),)),
        # Invalid: wrong check digit
        ("65070803A012", 0, ()),
        ("65070803A010", 0, ()),
        # Invalid: invalid month (00 or 13+)
        ("65070003A018", 0, ()),
        ("65071303A018", 0, ()),
        # Invalid: digit at position 9 instead of letter
        ("650708030018", 0, ()),
        # Too short / too long
        ("65070803A01",  0, ()),
        ("65070803A0180", 0, ()),
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
        # Valid
        ("65070803A018", True),
        # Wrong check digit
        ("65070803A012", False),
        ("65070803A010", False),
        # Digit instead of letter at position 9
        ("650708030018", False),
        # Wrong length
        ("65070803A01",  False),
        ("65070803A0180", False),
    ],
)
def test_when_de_social_security_validated_then_checksum_result_is_correct(
    number, expected, recognizer
):
    assert recognizer.validate_result(number) == expected
