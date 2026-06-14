"""
Tests for DeHealthInsuranceRecognizer (Krankenversicherungsnummer / KVNR).

Format: 10 characters – 1 uppercase letter (birth surname initial) +
8 digits (birth date + serial) + 1 check digit.

Valid numbers are generated with the GKV-Spitzenverband Prüfziffer algorithm
per § 290 SGB V Anlage 1 (Stand 02.01.2023): letter expanded to 2-digit
ordinal, alternating factors [1,2,1,2,1,2,1,2,1,2], products digit-summed
if ≥ 10 (Quersumme), sum mod 10.

Legal basis: § 290 SGB V.  DSGVO Art. 9 (Gesundheitsdaten).

Pre-calculated valid examples:
  A000500015  – from § 290 SGB V Anlage 1 (Hauptversicherter, PZ=5)
  C000500021  – from § 290 SGB V Anlage 1 (Familienversicherter IK part, PZ=1)
  A123456780  – letter A (=01), data 12345678, check = 0
  B123456782  – letter B (=02), data 12345678, check = 2
  M123456785  – letter M (=13), data 12345678, check = 5
  Z000000005  – letter Z (=26), exercises upper-bound letter ordinal
  Z999999997  – letter Z with all-9 data, exercises Quersumme on 7 of 10 products
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
        ("A000500015", 1, ((0, 10),)),
        ("C000500021", 1, ((0, 10),)),
        ("A123456780", 1, ((0, 10),)),
        ("M123456785", 1, ((0, 10),)),
        ("B123456782", 1, ((0, 10),)),
        # Edge: letter Z (upper bound of ordinal) and worst-case Quersumme density
        ("Z000000005", 1, ((0, 10),)),
        ("Z999999997", 1, ((0, 10),)),
        ("Krankenkasse KVNR: A123456780", 1, ((19, 29),)),
        ("eGK-Nummer M123456785 bitte angeben.", 1, ((11, 21),)),
        # Invalid: wrong check digit
        ("A123456787", 0, ()),
        ("M123456789", 0, ()),
        # Invalid: starts with digit instead of letter
        ("1123456780", 0, ()),
        # Lowercase: Presidio uses global IGNORECASE; validate_result calls .upper()
        # so a valid lowercase KVNR is matched and validated correctly
        ("a123456780", 1, ((0, 10),)),
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
        # Valid – official § 290 SGB V Anlage 1 samples
        ("A000500015", True),
        ("C000500021", True),
        # Valid – pre-computed fixtures
        ("A123456780", True),
        ("M123456785", True),
        ("B123456782", True),
        # Edge: letter Z (=26) exercises upper-bound ordinal; all-9 data
        # forces Quersumme on 7 of 10 products
        ("Z000000005", True),
        ("Z999999997", True),
        # Wrong check digit
        ("A123456787", False),
        ("M123456789", False),
        ("A000500010", False),
        # Starts with digit (after .upper() it's still a digit → re.match fails)
        ("1123456780", False),
        # Wrong length
        ("A12345678",  False),
        ("A1234567890", False),
        # Lowercase: .upper() converts to valid → True (IGNORECASE is global)
        ("a123456780", True),
    ],
)
def test_when_de_health_insurance_validated_then_checksum_result_is_correct(
    number, expected, recognizer
):
    assert recognizer.validate_result(number) == expected
