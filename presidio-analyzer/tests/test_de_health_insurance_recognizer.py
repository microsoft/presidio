"""
Tests for DeHealthInsuranceRecognizer (Krankenversicherungsnummer / KVNR).

Format: 10 characters – 1 uppercase letter (birth surname initial) +
8 digits (birth date + serial) + 1 check digit.

Valid numbers are generated with the GKV-Spitzenverband checksum algorithm
(letter expanded to 2-digit ordinal, weights [2,9,8,7,6,5,4,3,2,1],
products digit-summed if ≥ 10, sum mod 10).

Legal basis: § 290 SGB V.  DSGVO Art. 9 (Gesundheitsdaten).

Pre-calculated valid examples (fictitious):
  A123456787  – letter A (=01), data 12345678, check = 7
  M123456789  – letter M (=13), data 12345678, check = 9
  B123456787  – letter B (=02), data 12345678, check = 7
"""
import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import DeHealthInsuranceRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeHealthInsuranceRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_HEALTH_INSURANCE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # fmt: off
        # Valid KVNR – checksum passes → result at MAX_SCORE
        ("A123456787", 1, ((0, 10),)),
        ("M123456789", 1, ((0, 10),)),
        ("B123456787", 1, ((0, 10),)),
        ("Krankenkasse KVNR: A123456787", 1, ((19, 29),)),
        ("eGK-Nummer M123456789 bitte angeben.", 1, ((11, 21),)),
        # Invalid: wrong check digit
        ("A123456780", 0, ()),
        ("M123456781", 0, ()),
        # Invalid: starts with digit instead of letter
        ("1123456787", 0, ()),
        # Lowercase: Presidio uses global IGNORECASE; validate_result calls .upper()
        # so a valid lowercase KVNR is matched and validated correctly
        ("a123456787", 1, ((0, 10),)),
        # Too short (9 chars)
        ("A12345678",  0, ()),
        # Too long (11 chars)
        ("A1234567890", 0, ()),
        # fmt: on
    ],
)
def test_when_all_de_health_insurance_numbers_then_succeed(
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
        ("A123456787", True),
        ("M123456789", True),
        ("B123456787", True),
        # Wrong check digit
        ("A123456780", False),
        ("M123456781", False),
        # Starts with digit (after .upper() it's still a digit → re.match fails)
        ("1123456787", False),
        # Wrong length
        ("A12345678",  False),
        ("A1234567890", False),
        # Lowercase: .upper() converts to valid → True (IGNORECASE is global)
        ("a123456787", True),
    ],
)
def test_when_de_health_insurance_validated_then_checksum_result_is_correct(
    number, expected, recognizer
):
    assert recognizer.validate_result(number) == expected
