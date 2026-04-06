"""
Tests for DeFuehrerscheinRecognizer (Führerscheinnummer).

Post-2013 EU-harmonized format (FeV Anlage 8, EU Directive 2006/126/EC):
  11 characters: 2 uppercase letters (Behördenkürzel, derived from the
                  Kfz-Zulassungskürzel of the issuing Kreis/Stadt, e.g. HH for
                  Hamburg, MU for Mühldorf/München, BO for Bochum, KO for Koblenz)
                + 8 digits (3-digit authority number + 5-digit sequential number)
                + 1 check character (uppercase letter or digit; algorithm not published)

Note: single-letter Kfz abbreviations (B Berlin, K Köln, M München as single chars)
are always used in combination as 2-char authority codes in the Führerschein system
(e.g. "BO", "MU", "KN").  Pure single-letter + digit combos like "B0" are NOT part
of the 2-letter authority code and are out of scope for this strict pattern.

Pre-2013 formats (locally defined, non-standardized) are out of scope.

Fictitious examples following the 11-character structure:
  BO12345678A  – issuing authority "BO" (Bochum), authority-nr 123, sequential 45678
  MU12345678B  – issuing authority "MU" (Mühldorf), authority-nr 123, sequential 45678
  HH98765432C  – issuing authority "HH" (Hamburg)
  KO12345678X  – issuing authority "KO" (Koblenz)
"""
import pytest

from presidio_analyzer.predefined_recognizers import DeFuehrerscheinRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeFuehrerscheinRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_FUEHRERSCHEIN"]


@pytest.mark.parametrize(
    "text, expected_len",
    [
        # fmt: off
        # Valid post-2013 format: 2 letters + 8 digits + 1 alphanumeric
        ("BO12345678A", 1),
        ("MU12345678B", 1),
        ("HH98765432C", 1),
        ("KO12345678X", 1),
        ("DO98765432Z", 1),
        # Check character can be a digit too
        ("GE123456780", 1),
        ("MU123456785", 1),
        # In running text
        ("Führerscheinnummer: BO12345678A", 1),
        ("Fahrerlaubnis MU12345678B wurde ausgestellt.", 1),
        # Lowercase: Presidio uses global IGNORECASE → also matches
        ("mu12345678b", 1),
        # --- Should NOT match ---
        # Too short: 10 chars (missing check character)
        ("BO12345678",  0),
        # Too long: 12 chars
        ("BO12345678AB", 0),
        # Starts with digit instead of two letters
        ("12345678901", 0),
        # Only one leading letter (3-letter forms are not part of strict pattern)
        ("B12345678A",  0),
        # fmt: on
    ],
)
def test_when_all_de_fuehrerschein_numbers_then_succeed(
    text, expected_len, recognizer, entities
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
