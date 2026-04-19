"""
Tests for DeVatIdRecognizer (Umsatzsteuer-Identifikationsnummer / USt-IdNr.).

Format: "DE" + 9 digits (11 characters total). The 9th digit is a check
digit derived via ISO 7064 Mod 11,10 (same algorithm as Steuer-IdNr.).

Legal basis: § 27a UStG.  Format documentation: BZSt.

Pre-calculated valid examples (check-digit-consistent, fictitious in the
sense that no specific entity is being identified):
  DE136695976  – python-stdnum test vector
  DE129273398  – python-stdnum test vector
  DE123456788  – computed: DE + prefix 12345678 yields check digit 8
  DE111111117  – computed: DE + prefix 11111111 yields check digit 7
"""
import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import DeVatIdRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeVatIdRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_VAT_ID"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # fmt: off
        # Valid USt-IdNr. — check digit consistent
        ("DE136695976", 1, ((0, 11),)),
        ("DE129273398", 1, ((0, 11),)),
        ("DE123456788", 1, ((0, 11),)),
        ("DE111111117", 1, ((0, 11),)),
        # In running text
        ("USt-IdNr.: DE136695976", 1, ((11, 22),)),
        ("Bitte angeben: DE129273398 auf der Rechnung.", 1, ((15, 26),)),
        # Wrong check digit — rejected
        ("DE123456789", 0, ()),
        ("DE987654321", 0, ()),
        ("DE100000001", 0, ()),
        # Wrong country prefix
        ("AT123456789", 0, ()),
        ("FR12345678901", 0, ()),
        # Lowercase prefix — IGNORECASE allows match, validate_result uppercases
        ("de136695976", 1, ((0, 11),)),
        # Too few / too many digits
        ("DE12345678",  0, ()),
        ("DE1234567890", 0, ()),
        # fmt: on
    ],
)
def test_when_all_de_vat_ids_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, max_score)


@pytest.mark.parametrize(
    "number, expected",
    [
        # Valid — ISO 7064 Mod 11,10
        ("DE136695976", True),
        ("DE129273398", True),
        ("DE123456788", True),
        ("DE111111117", True),
        # Lowercase — upper() path
        ("de136695976", True),
        # Wrong check digit
        ("DE123456789", False),
        ("DE987654321", False),
        ("DE100000001", False),
        # Wrong length / format
        ("DE12345678", False),
        ("DE1234567890", False),
        ("AT123456789", False),
    ],
)
def test_when_de_vat_id_validated_then_checksum_result_is_correct(
    number, expected, recognizer
):
    assert recognizer.validate_result(number) == expected
