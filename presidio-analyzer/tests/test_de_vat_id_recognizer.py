"""
Tests for DeVatIdRecognizer (Umsatzsteuer-Identifikationsnummer / USt-IdNr.).

Format: "DE" + 9 digits (11 characters total). The 9th digit is
**conventionally** derived via ISO 7064 Mod 11,10 (same engine as
DE_TAX_ID), but this algorithm is NOT officially published by the BZSt.
The recognizer therefore runs in **heuristic mode by default**: a
structural-pass / checksum-fail input returns None (match kept at pattern
score) instead of False (match dropped). Strict mode can be opted into
via the constructor parameter ``strict_checksum=True``.

Legal basis: § 27a UStG.  Format documentation: BZSt.

Pre-calculated valid examples (check-digit-consistent, fictitious in the
sense that no specific entity is being identified):
  DE136695976  – python-stdnum test vector
  DE129273398  – python-stdnum test vector
  DE123456788  – computed: DE + prefix 12345678 yields check digit 8
  DE111111117  – computed: DE + prefix 11111111 yields check digit 7

Real-world formatting variants that must normalise to a valid ID:
  "DE 136 695 976", "DE-136-695-976", "DE.136.695.976", "DE 136695976",
  lowercase variants.
"""
import pytest

from tests import assert_result
from presidio_analyzer.predefined_recognizers import DeVatIdRecognizer


@pytest.fixture(scope="module")
def recognizer():
    """Default recognizer — heuristic mode (strict_checksum=False)."""
    return DeVatIdRecognizer()


@pytest.fixture(scope="module")
def strict_recognizer():
    """Strict recognizer — rejects on checksum mismatch."""
    return DeVatIdRecognizer(strict_checksum=True)


@pytest.fixture(scope="module")
def entities():
    return ["DE_VAT_ID"]


# ---------------------------------------------------------------------------
# analyze() — default (heuristic / non-strict) mode
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text, expected_len",
    [
        # fmt: off
        # Valid USt-IdNr — continuous form, checksum passes.
        ("DE136695976", 1),
        ("DE129273398", 1),
        ("DE123456788", 1),
        ("DE111111117", 1),
        # In running text
        ("USt-IdNr.: DE136695976", 1),
        ("Bitte angeben: DE129273398 auf der Rechnung.", 1),
        # Heuristic-mode default: invalid checksum but valid structure
        # → match kept (pattern score), NOT dropped.
        # This is the enterprise-safe behaviour: the BZSt algorithm is not
        # published, so a spec-divergent real USt-IdNr would still surface.
        ("DE123456789", 1),
        ("DE987654321", 1),
        ("DE100000001", 1),
        # Lowercase prefix — IGNORECASE + upper() in validate_result
        ("de136695976", 1),
        # Structural failures — dropped in every mode
        ("AT123456789", 0),      # wrong country
        ("FR12345678901", 0),    # wrong country
        ("DE12345678",   0),     # too short
        ("DE1234567890", 0),     # too long
        # fmt: on
    ],
)
def test_when_de_vat_ids_in_default_mode_then_heuristic_preserves_recall(
    text, expected_len, recognizer, entities
):
    """
    Default mode MUST NOT drop structurally-valid USt-IdNrs that only fail
    the unpublished checksum — this is the core false-negative protection.
    """
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len


# ---------------------------------------------------------------------------
# analyze() — real-world formatting robustness (normalisation)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text, expected_len",
    [
        # fmt: off
        # Space-separated (common on invoices and Impressum pages)
        ("DE 136 695 976", 1),
        ("DE 129 273 398", 1),
        # Single-space variant
        ("DE 136695976", 1),
        # Dash-separated
        ("DE-136-695-976", 1),
        # Dot-separated
        ("DE.136.695.976", 1),
        # Mixed separators (seen on poorly formatted PDFs)
        ("DE 136-695.976", 1),
        # Lowercase + separators combined
        ("de 136 695 976", 1),
        # In running text with separators
        ("Rechnung USt-IdNr. DE 136 695 976 von Beispiel GmbH", 1),
        # fmt: on
    ],
)
def test_when_de_vat_ids_with_real_world_formatting_then_normalization_succeeds(
    text, expected_len, recognizer, entities
):
    """
    The recognizer MUST detect USt-IdNrs regardless of whitespace, dashes,
    or dots — these appear routinely in real-world invoice/Impressum text.
    """
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len


# ---------------------------------------------------------------------------
# analyze() — strict mode
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text, expected_len",
    [
        # fmt: off
        # Valid ID still passes in strict mode
        ("DE136695976", 1),
        ("DE129273398", 1),
        # Invalid checksum IS dropped in strict mode (opt-in precision)
        ("DE123456789", 0),
        ("DE987654321", 0),
        ("DE100000001", 0),
        # Structural failures — still dropped
        ("AT123456789", 0),
        ("DE12345678",  0),
        # fmt: on
    ],
)
def test_when_de_vat_ids_in_strict_mode_then_checksum_is_enforced(
    text, expected_len, strict_recognizer, entities
):
    """
    strict_checksum=True MUST reject structurally-valid inputs that fail
    the ISO 7064 Mod 11,10 check. Use when precision > recall.
    """
    results = strict_recognizer.analyze(text, entities)
    assert len(results) == expected_len


# ---------------------------------------------------------------------------
# Positional / max_score assertions on verified-valid inputs
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text, expected_positions",
    [
        ("DE136695976", ((0, 11),)),
        ("DE 136 695 976", ((0, 14),)),
        ("USt-IdNr.: DE136695976", ((11, 22),)),
    ],
)
def test_when_valid_de_vat_id_then_max_score_and_correct_span(
    text, expected_positions, recognizer, entities, max_score
):
    results = recognizer.analyze(text, entities)
    assert len(results) == len(expected_positions)
    for res, (st, fn) in zip(results, expected_positions):
        assert_result(res, entities[0], st, fn, max_score)


# ---------------------------------------------------------------------------
# validate_result() — tri-state semantics
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "number, expected",
    [
        # Valid ISO 7064 Mod 11,10 → True
        ("DE136695976", True),
        ("DE129273398", True),
        ("DE123456788", True),
        ("DE111111117", True),
        # Normalisation paths → True
        ("de136695976", True),
        ("DE 136 695 976", True),
        ("DE-136-695-976", True),
        ("DE.136.695.976", True),
        ("de 136-695.976", True),
        # Structural failure → False (unambiguous, same in every mode)
        ("DE12345678", False),
        ("DE1234567890", False),
        ("AT123456789", False),
        ("", False),
        ("DEabcdefghi", False),
        # Checksum failure, DEFAULT mode → None (keep match at pattern score)
        ("DE123456789", None),
        ("DE987654321", None),
        ("DE100000001", None),
    ],
)
def test_when_de_vat_id_validated_in_default_mode_then_tri_state(
    number, expected, recognizer
):
    """
    validate_result in heuristic mode returns tri-state:
      True  — checksum passes
      None  — checksum fails but structure is valid (don't drop)
      False — structural failure
    """
    assert recognizer.validate_result(number) == expected


@pytest.mark.parametrize(
    "number, expected",
    [
        # Valid → True (same as default)
        ("DE136695976", True),
        ("DE 136 695 976", True),
        # Structural failure → False (same as default)
        ("DE12345678", False),
        ("AT123456789", False),
        # Checksum failure → False in strict mode (differs from default)
        ("DE123456789", False),
        ("DE987654321", False),
        ("DE100000001", False),
    ],
)
def test_when_de_vat_id_validated_in_strict_mode_then_checksum_is_enforced(
    number, expected, strict_recognizer
):
    """
    validate_result in strict mode downgrades the None arm to False, so
    checksum failures drop the match like structural failures do.
    """
    assert strict_recognizer.validate_result(number) == expected
