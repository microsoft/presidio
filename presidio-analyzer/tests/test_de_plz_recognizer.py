"""
Tests for DePlzRecognizer (Postleitzahl).

IMPORTANT: The base confidence is 0.05 due to the extreme false-positive risk of
matching any 5-digit number. These tests verify the regex structure (valid range,
boundary matching) only. In production, context words are required for the
recognizer to produce actionable (high-confidence) results.
"""
import pytest

from presidio_analyzer.predefined_recognizers import DePlzRecognizer
from tests import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    return DePlzRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["DE_PLZ"]


@pytest.mark.parametrize(
    "text, expected_len",
    [
        # fmt: off
        # --- Valid PLZ: range 01001–99998 ---
        ("10115", 1),   # Berlin Mitte
        ("80331", 1),   # München
        ("22085", 1),   # Hamburg
        ("01001", 1),   # minimum valid (leading zero)
        ("99998", 1),   # near-maximum
        # In running text (low confidence, context-free)
        ("PLZ: 10115", 1),
        ("Postleitzahl 80331 München", 1),
        # --- Should NOT match ---
        # 00000 is not a valid PLZ (excluded by regex)
        ("00000", 0),
        # 01000 and 99999 are boundary values outside the valid range
        ("01000", 0),
        ("99999", 0),
        # 6 digits → no match (word boundary)
        ("101150", 0),
        # 4 digits
        ("1011",  0),
        # fmt: on
    ],
)
def test_when_all_de_plz_then_succeed(text, expected_len, recognizer, entities):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len


@pytest.mark.parametrize(
    "text, expected_len, expected_start, expected_end",
    [
        # fmt: off
        ("10115", 1, 0, 5),
        ("PLZ 80331", 1, 4, 9),
        # fmt: on
    ],
)
def test_when_de_plz_matched_then_position_is_correct(
    text, expected_len, expected_start, expected_end, recognizer, entities
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    if expected_len > 0:
        assert_result_within_score_range(
            results[0], entities[0], expected_start, expected_end, 0.0, 0.5
        )
