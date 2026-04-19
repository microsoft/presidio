"""
Tests for DeBsnrRecognizer (Betriebsstättennummer / BSNR).

Format: 9 digits — 2-digit KV Bereichskennzeichen (regional KV code)
+ 7 sequential digits. No public checksum; validate_result uses the KV
regional-code whitelist per KBV Arztnummern-Richtlinie Anlage 1.

Legal basis: § 75 Abs. 7 SGB V; KBV-Richtlinie zur Vergabe der Arzt-,
Betriebsstätten-, Praxisnetz- sowie Netzverbundnummern.

Fictitious examples with valid KV prefixes:
  021234568  – 02 Hamburg
  521234567  – 52 Baden-Württemberg
  711234567  – 71 Bayern
  351234567  – 35 Krankenhäuser (Anlage 8 BMV-Ä)
"""
import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import DeBsnrRecognizer


@pytest.fixture(scope="module")
def recognizer():
    return DeBsnrRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_BSNR"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions",
    [
        # fmt: off
        # Valid KV prefix → validate_result returns True → high confidence
        ("021234568", 1, ((0, 9),)),
        ("521234567", 1, ((0, 9),)),
        ("711234567", 1, ((0, 9),)),
        ("351234567", 1, ((0, 9),)),
        # In running text
        ("Betriebsstättennummer: 021234568", 1, ((23, 32),)),
        ("BSNR 711234567 der Praxis.", 1, ((5, 14),)),
        # Unknown KV prefix → validate_result returns None → pattern score only
        # Still matches, but at lower confidence
        ("991234567", 1, ((0, 9),)),
        # All-zero → validate_result returns False → dropped
        ("000000000", 0, ()),
        # Too short (8 digits)
        ("02123456",  0, ()),
        # Too long (10 digits)
        ("0212345689", 0, ()),
        # Non-numeric
        ("02123456A", 0, ()),
        # fmt: on
    ],
)
def test_when_all_de_bsnr_numbers_then_succeed(
    text, expected_len, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len


@pytest.mark.parametrize(
    "number, expected",
    [
        # Valid KV prefixes
        ("021234568", True),   # 02 Hamburg
        ("521234567", True),   # 52 Baden-Württemberg
        ("711234567", True),   # 71 Bayern
        ("351234567", True),   # 35 Krankenhäuser
        ("741234567", True),   # 74 KBV
        # Unknown prefix — None, could be historic
        ("991234567", None),
        ("051234567", None),
        # Clearly invalid
        ("000000000", False),
        ("02123456",  False),  # 8 digits
        ("0212345689", False), # 10 digits
        ("02123456A", False),  # non-numeric
    ],
)
def test_when_de_bsnr_validated_then_result_is_correct(
    number, expected, recognizer
):
    assert recognizer.validate_result(number) == expected
