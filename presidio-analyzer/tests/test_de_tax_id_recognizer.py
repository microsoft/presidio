"""
Tests for DeTaxIdRecognizer (Steueridentifikationsnummer).

All test numbers are fictitious/generated and do not represent real persons.
Valid numbers are produced with the official ISO 7064 Mod 11, 10 algorithm
as specified by the Bundeszentralamt für Steuern (§§ 139a–139e AO).
"""
import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import DeTaxIdRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeTaxIdRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_TAX_ID"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # fmt: off
        # Valid Steuer-IdNr – checksum passes → result at MAX_SCORE
        ("12345678903", 1, ((0, 11),)),
        ("98765432106", 1, ((0, 11),)),
        ("Meine Steuer-ID: 12345678903.", 1, ((17, 28),)),
        ("IdNr. 98765432106 liegt vor.", 1, ((6, 17),)),
        # Invalid: wrong check digit
        ("12345678901", 0, ()),
        ("98765432100", 0, ()),
        # Invalid: leading zero (first digit must be 1–9)
        ("02345678901", 0, ()),
        # Invalid: too short / too long
        ("1234567890",  0, ()),
        ("123456789030", 0, ()),
        # Invalid: all ten leading digits are identical (excluded by spec)
        ("11111111111", 0, ()),
        # fmt: on
    ],
)
def test_when_all_de_tax_ids_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)


@pytest.mark.parametrize(
    "number, expected",
    [
        # Valid numbers
        ("12345678903", True),
        ("98765432106", True),
        # Wrong check digit
        ("12345678901", False),
        ("98765432100", False),
        # Leading zero
        ("02345678903", False),
        # Non-numeric
        ("abcdefghijk", False),
        # Wrong length
        ("1234567890",  False),
        ("123456789030", False),
        # All same first 10 digits
        ("11111111111", False),
    ],
)
def test_when_de_tax_id_validated_then_checksum_result_is_correct(number, expected, recognizer):
    assert recognizer.validate_result(number) == expected
