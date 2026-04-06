"""
Tests for DeVatIdRecognizer (Umsatzsteuer-Identifikationsnummer / USt-IdNr.).

Format: "DE" + 9 digits (11 characters total).

Legal basis: § 27a UStG.  Format documentation: BZSt.

Fictitious examples:
  DE123456789
  DE987654321
  DE100000001
"""
import pytest

from presidio_analyzer.predefined_recognizers import DeVatIdRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeVatIdRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_VAT_ID"]


@pytest.mark.parametrize(
    "text, expected_len",
    [
        # fmt: off
        # Valid format: DE + 9 digits
        ("DE123456789", 1),
        ("DE987654321", 1),
        ("DE100000001", 1),
        # In running text
        ("USt-IdNr.: DE123456789", 1),
        ("Bitte angeben: DE987654321 auf der Rechnung.", 1),
        # Wrong country prefix – must not match
        ("AT123456789", 0),
        ("FR12345678901", 0),
        # Lowercase prefix – Presidio uses global IGNORECASE
        ("de123456789", 1),
        # Too few digits (8)
        ("DE12345678",  0),
        # Too many digits (10)
        ("DE1234567890", 0),
        # fmt: on
    ],
)
def test_when_all_de_vat_ids_then_succeed(
    text, expected_len, recognizer, entities
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
