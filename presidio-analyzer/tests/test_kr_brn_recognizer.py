import pytest

from tests import assert_result_within_score_range
from presidio_analyzer.predefined_recognizers.country_specific.korea import KrBrnRecognizer

@pytest.fixture(scope="module")
def recognizer():
    return KrBrnRecognizer()

@pytest.fixture(scope="module")
def entities():
    return ["KR_BRN"]

@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid BRNs (Checksum pass) ---
        ("104-86-56659", 1, ((0, 12),), ((1.0, 1.0),), ),
        ("1048656659", 1, ((0, 10),), ((1.0, 1.0),), ),
        ("104-82-13138", 1, ((0, 12),), ((1.0, 1.0),), ),
        ("My BRN is 1048656659", 1, ((10, 20),), ((1.0, 1.0),), ),

        # Invalid BRNs (Checksum fail or Invalid format) ---
        # Correct format but wrong checksum
        ("104-86-56658", 0, (), (),),
        # Too short
        ("110-81-4127", 0, (), (),),
        # Too long
        ("110-81-412722", 0, (), (),),
        # Contains letters
        ("110-81-4127A", 0, (), (),),
        # Random numbers that fail checksum
        ("123-45-67890", 0, (), (),),
    ],
)
def test_when_all_brns_then_succeed(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
    max_score,
):
    results = recognizer.analyze(text, entities)
    assert len(results) == expected_len
    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        if fn_score == "max":
            fn_score = max_score
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )
