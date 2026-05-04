"""
Tests for DeBsnrRecognizer (Betriebsstättennummer / BSNR).

Format: 9 digits — 2-digit KV Bereichskennzeichen (regional KV code)
+ 7 sequential digits. No publicly documented Prüfziffer algorithm
exists, so validate_result only rejects clearly-invalid inputs (wrong
length, non-digit, all-zero) and returns None for every other 9-digit
input. Context words drive final confidence via the enhancer.

Legal basis: § 75 Abs. 7 SGB V; KBV-Richtlinie zur Vergabe der Arzt-,
Betriebsstätten-, Praxisnetz- sowie Netzverbundnummern.

Fictitious examples with valid KV prefixes (per Arztnummern-Richtlinie
Anlage 1, kept here so readers see the expected range even though the
recognizer no longer differentiates whitelisted vs. unknown prefixes):
  021234568  – 02 Hamburg
  521234567  – 52 Baden-Württemberg
  711234567  – 71 Bayern
  351234567  – 35 Krankenhäuser (Anlage 8 BMV-Ä)
"""
import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import DeBsnrRecognizer

# Pattern score from DeBsnrRecognizer.PATTERNS.  validate_result returns
# None on all structurally-valid inputs, so matches keep this score.
_PATTERN_SCORE = 0.2


@pytest.fixture(scope="module")
def recognizer():
    return DeBsnrRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_BSNR"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score",
    [
        # fmt: off
        # Valid KV prefix → None → pattern score
        ("021234568", 1, ((0, 9),), _PATTERN_SCORE),
        ("521234567", 1, ((0, 9),), _PATTERN_SCORE),
        ("711234567", 1, ((0, 9),), _PATTERN_SCORE),
        ("351234567", 1, ((0, 9),), _PATTERN_SCORE),
        # In running text — still pattern score on the bare number; the
        # ContextAwareEnhancer would boost this in a full pipeline but we
        # test the recognizer in isolation here.
        ("Betriebsstättennummer: 021234568", 1, ((23, 32),), _PATTERN_SCORE),
        ("BSNR 711234567 der Praxis.", 1, ((5, 14),), _PATTERN_SCORE),
        # Unknown / non-whitelisted prefix → None → pattern score too
        # (post-review behaviour: the whitelist is documentation, not a
        # confidence gate)
        ("991234567", 1, ((0, 9),), _PATTERN_SCORE),
        ("051234567", 1, ((0, 9),), _PATTERN_SCORE),
        # All-zero → False → dropped
        ("000000000", 0, (), None),
        # Too short / too long → dropped
        ("02123456",  0, (), None),
        ("0212345689", 0, (), None),
        # Non-numeric → dropped
        ("02123456A", 0, (), None),
        # fmt: on
    ],
)
def test_when_all_de_bsnr_numbers_then_succeed(
    text, expected_len, expected_positions, expected_score,
    recognizer, entities,
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos) in zip(results, expected_positions):
        assert_result(res, entities[0], st_pos, fn_pos, expected_score)


@pytest.mark.parametrize(
    "number, expected",
    [
        # Structurally valid — always None (no public checksum exists)
        ("021234568", None),   # whitelisted prefix 02 Hamburg
        ("521234567", None),   # whitelisted prefix 52 Baden-Württemberg
        ("711234567", None),   # whitelisted prefix 71 Bayern
        ("351234567", None),   # whitelisted prefix 35 Krankenhäuser
        ("741234567", None),   # whitelisted prefix 74 KBV
        ("991234567", None),   # non-whitelisted but structurally valid
        ("051234567", None),
        # Structurally invalid — False
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
