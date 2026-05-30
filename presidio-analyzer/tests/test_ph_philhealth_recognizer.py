"""Tests for PhPhilhealthRecognizer."""

# ruff: noqa: D103

import time

import pytest
from presidio_analyzer.predefined_recognizers import PhPhilhealthRecognizer

from tests import assert_result_within_score_range


@pytest.fixture(scope="module")
def recognizer():
    return PhPhilhealthRecognizer()


@pytest.fixture(scope="module")
def entities():
    return ["PH_HEALTH_INSURANCE"]


@pytest.mark.parametrize(
    "text, expected_len, expected_positions, expected_score_ranges",
    [
        # fmt: off
        # Valid PhilHealth PINs. Checksum passes.
        ("12-000015726-6", 1, ((0, 14),), ((0.5, 0.5),)),
        ("120000157266", 1, ((0, 12),), ((0.1, 0.1),)),
        ("PhilHealth# 12-000015726-6", 1, ((12, 26),), ((0.5, 1.0),)),
        ("PIN: 120000157266", 1, ((5, 17),), ((0.1, 1.0),)),
        ("Seguro 12-000015726-6 confirmed.", 1, ((7, 21),), ((0.5, 1.0),)),
        # Invalid: correct shape but wrong check digit.
        ("12-000015726-7", 0, (), ()),
        ("120000157267", 0, (), ()),
        # Invalid: too short, too long, or malformed separators.
        ("12-00001572-6", 0, (), ()),
        ("1200001572669", 0, (), ()),
        ("12 000015726 6", 0, (), ()),
        # fmt: on
    ],
)
def test_when_philhealth_pin_in_text_then_all_ph_health_insurance_found(
    text,
    expected_len,
    expected_positions,
    expected_score_ranges,
    recognizer,
    entities,
):
    results = recognizer.analyze(text, entities)

    assert len(results) == expected_len
    for res, (st_pos, fn_pos), (st_score, fn_score) in zip(
        results, expected_positions, expected_score_ranges
    ):
        assert_result_within_score_range(
            res, entities[0], st_pos, fn_pos, st_score, fn_score
        )


@pytest.mark.parametrize(
    "number, expected",
    [
        ("12-000015726-6", True),
        ("120000157266", True),
        ("12-000015726-7", False),
        ("120000157267", False),
        ("12-00001572-6", False),
        ("1200001572669", False),
        ("12 000015726 6", True),
    ],
)
def test_when_philhealth_pin_validated_then_checksum_result_is_correct(
    number, expected, recognizer
):
    digits = recognizer._normalize(number)
    assert recognizer._is_valid_pin(digits) is expected


def test_performance(recognizer, entities):
    text = "PhilHealth number 12-000015726-6 was verified. " * 4
    start = time.time()

    recognizer.analyze(text, entities)

    elapsed = (time.time() - start) * 1000
    assert elapsed < 100, f"Too slow: {elapsed:.1f}ms"
